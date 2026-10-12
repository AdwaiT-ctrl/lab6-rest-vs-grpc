# REST and gRPC comparison

## GCP measurements

All RPC entries are mean milliseconds per operation. PING entries are mean round-trip times in milliseconds. Local and same-zone measurements use 1,000 calls per method; different-region measurements use 100. Each benchmark performs five untimed warmup calls and verifies the responses.

| Method | Local | Same-Zone | Different Region |
|---|---:|---:|---:|
| REST add | 2.432 | 4.035 | 314.685 |
| gRPC add | 0.815 | 1.363 | 284.978 |
| REST rawimg | 4.314 | 24.402 | 1258.875 |
| gRPC rawimg | 7.910 | 12.485 | 418.617 |
| REST dotproduct | 2.735 | 3.839 | 319.346 |
| gRPC dotproduct | 0.944 | 1.702 | 141.009 |
| REST jsonimg | 17.928 | 30.680 | 1684.096 |
| gRPC jsonimg | 23.529 | 35.819 | 430.919 |
| PING | 0.060 | 0.457 | 377.836 |

## Experimental configuration

The following configuration was used for the supplied measurements:

| VM | Role | Zone | Machine type | Internal IP |
|---|---|---|---|---|
| lab6-client | All clients; localhost servers | us-west1-a | e2-medium | 10.138.0.16 |
| lab6-server-west | Same-zone servers | us-west1-a | e2-medium | 10.138.0.17 |
| lab6-server-europe | Different-region servers | europe-west2-a (London) | e2-medium | 10.154.0.2 |

Both transports use the same supplied JPEG and two length-100 random vectors generated with the same seed. Payload loading and preparation are outside the timed loop. REST creates a new Session/TCP connection for every request; gRPC reuses one ready channel. Timings include the synchronous request, server processing, response, and response parsing. Images are opened to inspect dimensions without decoding all pixels.

Raw RPC data are preserved in measurements/local.csv, measurements/same-zone.csv, and measurements/different-region.csv. The ping files contain the summary lines supplied from the VM runs. The different-region CSV includes an earlier REST add result of 506.834 ms and a later result of 314.685 ms. The table uses the later entry, which accompanies the complete eight-method sequence; both entries remain in the raw CSV.

## Performance observations

For the small add and dotproduct requests, gRPC was faster than REST in all three scenarios. Network latency becomes a major part of the different-region measurements: small local calls take about 0.8–2.7 ms, whereas the corresponding different-region calls take about 141–319 ms. Opening a new TCP connection per REST call introduces handshake overhead, while gRPC's reused channel avoids repeated connection establishment. Large different-region images also favor gRPC: raw images took 418.617 ms versus REST's 1258.875 ms, and base64 images took 430.919 ms versus REST's 1684.096 ms. However, gRPC was not universally faster: REST was faster for local raw and base64 images and for same-zone base64 images. These results reflect the combined effects of connection handling, serialization, buffering, server implementation, and network conditions; the measurements do not isolate each cost.

Base64 expands the 1,655,274-byte JPEG to 2,207,032 bytes before field overhead, about a 33.3% increase. Base64 image calls were slower than raw image calls for both transports in every scenario. Protobuf also reduced the dotproduct request payload from 4,075 bytes for JSON to 1,606 bytes. The recorded byte counts are application payload sizes, excluding transport headers, framing, and responses; they are not measurements of wire bandwidth.

The ping samples were collected separately from the RPC runs. In particular, the different-region ping mean of 377.836 ms exceeds some RPC averages, so it cannot be treated as a simultaneous baseline or subtracted from those timings to estimate Python overhead. Network conditions or paths may have differed between samples; the provided data do not establish the cause. The earlier and later different-region REST add results also show variability between runs.
