cd ..
protoc \
  --proto_path=./protocol \
  --js_out=import_style=commonjs,binary:src/proto \
  --grpc-web_out=import_style=commonjs,mode=grpcwebtext:src/proto \
  --js_out=import_style=commonjs,binary:service/proto \
  --plugin=protoc-gen-grpc=`which grpc_tools_node_protoc_plugin` \
  api.proto
