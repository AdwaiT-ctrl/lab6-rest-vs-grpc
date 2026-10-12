#!/usr/bin/env python3
import argparse
from concurrent import futures
import grpc
import lab6_pb2 as pb
import lab6_pb2_grpc as rpc
from operations import decode_image, dot_product, image_dimensions

OPTIONS = [('grpc.max_receive_message_length', 32 * 1024 * 1024),
           ('grpc.max_send_message_length', 32 * 1024 * 1024)]


class Lab6Service(rpc.Lab6Servicer):
    def Add(self, request, context):
        result = request.a + request.b
        if not -(2**31) <= result < 2**31:
            context.abort(grpc.StatusCode.INVALID_ARGUMENT, 'sum is outside int32 range')
        return pb.AddReply(sum=result)

    def RawImage(self, request, context):
        try:
            return pb.ImageReply(**image_dimensions(request.img))
        except ValueError as exc:
            context.abort(grpc.StatusCode.INVALID_ARGUMENT, str(exc))

    def DotProduct(self, request, context):
        try:
            return pb.DotProductReply(dotproduct=dot_product(list(request.a), list(request.b)))
        except ValueError as exc:
            context.abort(grpc.StatusCode.INVALID_ARGUMENT, str(exc))

    def JsonImage(self, request, context):
        try:
            return pb.ImageReply(**image_dimensions(decode_image(request.img)))
        except ValueError as exc:
            context.abort(grpc.StatusCode.INVALID_ARGUMENT, str(exc))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Lab 6 gRPC server')
    parser.add_argument('-p', '--port', type=int, default=50051)
    parser.add_argument('--host', default='0.0.0.0')
    args = parser.parse_args()
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10), options=OPTIONS)
    rpc.add_Lab6Servicer_to_server(Lab6Service(), server)
    if not server.add_insecure_port(f'{args.host}:{args.port}'):
        raise RuntimeError('could not bind gRPC port')
    server.start()
    print(f'gRPC server listening on {args.host}:{args.port}', flush=True)
    try:
        server.wait_for_termination()
    except KeyboardInterrupt:
        server.stop(0).wait()
