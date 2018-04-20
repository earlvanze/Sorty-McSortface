help:
	@fgrep -h "##" $(MAKEFILE_LIST) | fgrep -v fgrep | sed -e 's/\\$$//' | sed -e 's/##//'

download_models:
	cd model && sh download.sh

download_ssd_mobilenets:
	rm -rf inference_graph
	wget -O inference_graph.tar.gz https://s3.amazonaws.com/sorty-ai/trained_models/ssd_mobilenet_v1_coco/v4/inference_graph.tar.gz
	tar -xzvf inference_graph.tar.gz
	rm -rf inference_graph.tar.gz

download_ssd_inception:
	rm -rf inference_graph
	wget -O inference_graph.tar.gz https://s3.amazonaws.com/sorty-ai/trained_models/ssd_inception_v2_coco/v1/inference_graph.tar.gz
	tar -xzvf inference_graph.tar.gz
	rm -rf inference_graph.tar.gz

.PHONY: clean

clean:
	find . -name '*.pyc' -exec rm -rf {} +
	find . -name '*__pycache__' -exec rm -rf {} +