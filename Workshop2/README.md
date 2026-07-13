# Advanced API Design: RESTful Standards & gRPC


## gRPC
install
pip install grpcio grpcio-tools

compile proto
python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. showcase.proto
