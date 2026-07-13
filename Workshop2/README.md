# Advanced API Design: RESTful Standards & gRPC
## Python
- pip install grpcio grpcio-tools
- python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. telemetry.proto

## Node.js
- npm install @grpc/grpc-js @grpc/proto-loader
