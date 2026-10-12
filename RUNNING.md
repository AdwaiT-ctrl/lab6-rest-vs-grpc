# Running the lab

All four methods are implemented for REST and gRPC. The main README's dotproduct requirement is used; the reference to "sum" in the gRPC details is interpreted as dotproduct. The protobuf uses doubles for vectors and the dot product to preserve the precision of Python random.random().

## Install and verify

Use Python 3.11 or newer. From this project directory:

```sh
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. lab6.proto
python -m unittest -v test_services
```

On Windows activate with .venv\Scripts\Activate.ps1, or call .venv\Scripts\python.exe directly. Alternatively, use uv sync and uv run for the commands. Generated lab6_pb2.py and lab6_pb2_grpc.py are included; requirements.txt and uv.lock match the tested dependencies.

## Servers and clients

Run each server in its own terminal:

```sh
python rest-server.py
python grpc-server.py
```

REST listens on port 5000 and gRPC on 50051. Both bind to all interfaces for the VM experiments. Each client accepts a hostname, method, and repetition count:

```sh
python rest-client.py localhost add 1000
python grpc-client.py localhost add 1000
python rest-client.py localhost dotproduct 1000 --debug
python grpc-client.py localhost jsonimage 1000 --debug
```

Supported methods: add, rawimage, dotproduct, jsonimage (case insensitive). Both clients support --port, --warmup, --timeout, --seed, --image, --csv, and --scenario.

## Required cloud experiments

Use three e2-standard-2 VMs in one VPC: a client/server VM and another server VM in us-west1-a, plus a server VM in europe-west3-a. Install the same dependencies and copy this entire project, including the supplied JPEG, onto each VM. Run both servers on each server VM. Ensure the VPC permits TCP 5000/50051 and ICMP from the client VM to server internal IPs.

From the us-west1-a client VM, run the following. Replace the IP placeholders with the actual 10.x.y.z server IPs:

```sh
python measure-all.py localhost local
ping -c 10 localhost > measurements/local-ping.txt
python measure-all.py SAME_ZONE_INTERNAL_IP same-zone
ping -c 10 SAME_ZONE_INTERNAL_IP > measurements/same-zone-ping.txt
python measure-all.py FRANKFURT_INTERNAL_IP different-region
ping -c 10 FRANKFURT_INTERNAL_IP > measurements/different-region-ping.txt
```

The helper defaults to 1000 calls per method locally and in the same zone, and 100 across regions. Copy the CSVs and ping logs back, fill the required table in SOLUTION.md with mean ms_per_operation and mean ping RTT, and update the observations with the actual cloud results. Record VM names, zones, machine types, internal IPs, and measurement date. Creating VMs may incur charges; no cloud resources have been created by this implementation.

## Measurement method

Both clients pre-load the same supplied JPEG and prepare payloads before timing. Each dotproduct uses two length-100 vectors produced by random.random(), with the same seed for both transports. Five untimed warmup calls are checked. The timed loop uses perf_counter and includes the synchronous request, server processing, response, and response parsing; response correctness is checked afterward. Failed calls stop the benchmark instead of contributing misleading timings.

REST deliberately uses a fresh requests.Session for each query, matching the assignment's connection model. gRPC waits for one channel to be ready and reuses it for all calls. Image servers open the image and inspect dimensions without decoding all pixels, matching the starter code. The payload byte count excludes HTTP headers, the add URL, gRPC framing, TCP/IP overhead, and responses; it is a payload comparison, not measured wire bandwidth. No transport compression is enabled.

The laptop-local CSV is development evidence and must not be substituted for the assignment's e2-standard-2 localhost experiment.
