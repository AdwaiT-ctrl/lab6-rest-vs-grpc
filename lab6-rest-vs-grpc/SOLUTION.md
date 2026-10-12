# REST and gRPC comparison

## Required GCP measurements — pending

The implementation is complete and locally verified. These experiments still require access to the specified Google Cloud VMs. Pending entries are unmeasured; they are not estimates. All times below are milliseconds per operation, except PING, which is mean round-trip time.

| Method | Local (us-west1-a VM) | Same-Zone (us-west1-a) | Different Region (europe-west3-a) |
|---|---|---|---|
| REST add | Pending | Pending | Pending |
| gRPC add | Pending | Pending | Pending |
| REST rawimg | Pending | Pending | Pending |
| gRPC rawimg | Pending | Pending | Pending |
| REST dotproduct | Pending | Pending | Pending |
| gRPC dotproduct | Pending | Pending | Pending |
| REST jsonimg | Pending | Pending | Pending |
| gRPC jsonimg | Pending | Pending | Pending |
| PING | Pending | Pending | Pending |

Run the commands in RUNNING.md on e2-standard-2 VMs using internal IP addresses to complete this table. The cloud performance observations must be finalized after those measurements.

## Supplemental laptop results

Measured on October 11, 2026, on Windows with Python 3.11. Both servers and clients ran on this computer through 127.0.0.1. Each RPC used 1000 measured calls after 5 warmups. Raw data: measurements/laptop-local.csv. These are laptop measurements, not the required cloud results.

| Method | Laptop localhost (ms/op) | Request payload (bytes) |
|---|---:|---:|
| REST add | 11.508 | 0 (arguments in URL) |
| gRPC add | 0.384 | 4 |
| REST rawimg | 27.523 | 1,655,274 |
| gRPC rawimg | 12.042 | 1,655,278 |
| REST dotproduct | 13.513 | 4,075 |
| gRPC dotproduct | 0.447 | 1,606 |
| REST jsonimg | 45.292 | 2,207,045 |
| gRPC jsonimg | 18.191 | 2,207,037 |
| PING | <1 ms for all 10 replies | — |

Windows ping reported 0 ms average because its output rounds sub-millisecond RTTs. This does not establish zero network latency. The JPEG is 1,655,274 bytes; base64 expands it to 2,207,032 bytes before JSON/protobuf field overhead. Payload sizes exclude transport headers and framing and do not measure wire bandwidth.

## Observations from the laptop experiment

On this laptop, gRPC was faster for all four operations. The largest relative differences were for add and dotproduct, where connection and serialization overhead dominate the small payload and inexpensive computation. This REST client establishes a new TCP connection for every query, while the gRPC client reuses a single channel. Higher network RTT should increase the cost of REST's repeated TCP handshakes; both transports still incur request/response latency. REST can also reuse connections with a persistent Session, so this comparison applies to the connection behavior required by this assignment. The image results show that larger payloads reduce the relative benefit of gRPC: transfer and buffer processing become more substantial. Base64 increased image payload size by about one third, and both base64 image methods were slower than their raw binary counterparts. Same-zone and cross-region effects have not yet been measured, so no claims about their actual timings are made here.
