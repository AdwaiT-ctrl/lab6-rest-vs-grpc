"""End-to-end parity and invalid-input tests (no external hosts required)."""
import base64
from concurrent import futures
import importlib.util
import io
import unittest
import grpc
from PIL import Image
import lab6_pb2 as pb
import lab6_pb2_grpc as rpc


def load(name, filename):
    spec = importlib.util.spec_from_file_location(name, filename)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class ServicesTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rest = load('rest_server', 'rest-server.py').app.test_client()
        cls.server = grpc.server(futures.ThreadPoolExecutor(max_workers=2))
        rpc.add_Lab6Servicer_to_server(load('grpc_server', 'grpc-server.py').Lab6Service(), cls.server)
        port = cls.server.add_insecure_port('127.0.0.1:0')
        cls.server.start()
        cls.channel = grpc.insecure_channel(f'127.0.0.1:{port}')
        cls.stub = rpc.Lab6Stub(cls.channel)
        buffer = io.BytesIO()
        Image.new('RGB', (13, 7)).save(buffer, format='PNG')
        cls.image = buffer.getvalue()

    @classmethod
    def tearDownClass(cls):
        cls.channel.close()
        cls.server.stop(0).wait()

    def test_add(self):
        self.assertEqual(self.rest.post('/api/add/-5/10').json, {'sum': 5})
        self.assertEqual(self.stub.Add(pb.AddRequest(a=-5, b=10), timeout=5).sum, 5)

    def test_dot_products(self):
        for a, b in [([], []), ([1, 2], [3, 4]), ([.1]*137, [.2]*137)]:
            expected = sum(x*y for x, y in zip(a, b))
            response = self.rest.post('/api/dotproduct', json={'a': a, 'b': b})
            self.assertEqual(response.status_code, 200)
            self.assertAlmostEqual(response.json['dotproduct'], expected)
            self.assertAlmostEqual(self.stub.DotProduct(pb.DotProductRequest(a=a, b=b), timeout=5).dotproduct, expected)

    def test_images(self):
        expected = {'width': 13, 'height': 7}
        encoded = base64.b64encode(self.image).decode('ascii')
        self.assertEqual(self.rest.post('/api/rawimage', data=self.image, content_type='image/png').json, expected)
        self.assertEqual(self.rest.post('/api/jsonimage', json={'image': encoded}).json, expected)
        for result in [self.stub.RawImage(pb.RawImageRequest(img=self.image), timeout=5),
                       self.stub.JsonImage(pb.JsonImageRequest(img=encoded), timeout=5)]:
            self.assertEqual((result.width, result.height), (13, 7))

    def test_invalid_rest_payloads(self):
        for body in [{'a': [1], 'b': []}, {'a': ['x'], 'b': [2]}, {'a': [True], 'b': [2]}, {}]:
            self.assertEqual(self.rest.post('/api/dotproduct', json=body).status_code, 400)
        for body in [{'image': '!!!'}, {'image': 12}, {}, []]:
            self.assertEqual(self.rest.post('/api/jsonimage', json=body).status_code, 400)
        self.assertEqual(self.rest.post('/api/rawimage', data=b'invalid').status_code, 400)
        self.assertEqual(self.rest.post('/api/dotproduct', data='{', content_type='application/json').status_code, 400)

    def test_invalid_grpc_payloads(self):
        for method, message in [(self.stub.DotProduct, pb.DotProductRequest(a=[1], b=[])),
                                (self.stub.DotProduct, pb.DotProductRequest(a=[float('nan')], b=[1])),
                                (self.stub.RawImage, pb.RawImageRequest(img=b'invalid')),
                                (self.stub.JsonImage, pb.JsonImageRequest(img='!!!')),
                                (self.stub.Add, pb.AddRequest(a=2**31-1, b=1))]:
            with self.assertRaises(grpc.RpcError) as caught:
                method(message, timeout=5)
            self.assertEqual(caught.exception.code(), grpc.StatusCode.INVALID_ARGUMENT)


if __name__ == '__main__':
    unittest.main()
