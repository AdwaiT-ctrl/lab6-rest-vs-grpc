#!/usr/bin/env python3
import grpc
import lab6_pb2 as pb
import lab6_pb2_grpc as rpc
from benchmark import arguments, measure, payload

OPTIONS = [('grpc.max_receive_message_length', 32 * 1024 * 1024),
           ('grpc.max_send_message_length', 32 * 1024 * 1024)]


def main():
    args = arguments('gRPC', 50051)
    data, expected = payload(args)
    if args.cmd == 'add':
        message, method = pb.AddRequest(**data), 'Add'
    elif args.cmd == 'dotproduct':
        message, method = pb.DotProductRequest(**data), 'DotProduct'
    elif args.cmd == 'rawimage':
        message, method = pb.RawImageRequest(img=data), 'RawImage'
    else:
        message, method = pb.JsonImageRequest(img=data['image']), 'JsonImage'
    with grpc.insecure_channel(f'{args.host}:{args.port}', options=OPTIONS) as channel:
        grpc.channel_ready_future(channel).result(timeout=args.timeout)
        remote = getattr(rpc.Lab6Stub(channel), method)

        def call():
            reply = remote(message, timeout=args.timeout)
            return {key: getattr(reply, key) for key in expected}

        measure(args, 'gRPC', call, expected, message.ByteSize())


if __name__ == '__main__':
    main()
