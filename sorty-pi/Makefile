help:           ## Show this help.
	@fgrep -h "##" $(MAKEFILE_LIST) | fgrep -v fgrep | sed -e 's/\\$$//' | sed -e 's/##//'

download_model: ## Download both ssd mobilenets and inception.
	cd model && sh download.sh

download_ssd_mobilenets: ## Download inference graph for mobilenets.
	rm -rf inference_graph
	wget -O inference_graph.tar.gz https://s3.amazonaws.com/sorty-ai/trained_models/ssd_mobilenet_v1_coco/v3/inference_graph.tar.gz
	tar -xzvf inference_graph.tar.gz
	rm -rf inference_graph.tar.gz

download_ssd_inception: ## Download inference graph for inception.
	rm -rf inference_graph
	wget -O inference_graph.tar.gz https://s3.amazonaws.com/sorty-ai/trained_models/ssd_inception_v2_coco/v1/inference_graph.tar.gz
	tar -xzvf inference_graph.tar.gz
	rm -rf inference_graph.tar.gz