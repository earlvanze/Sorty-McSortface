# Getting started

### Setup AWS configs

```bash
# setup your config.ini file
[AWS]
AWS_ACCESS_KEY_ID = AWS_ACCESS_KEY_ID
AWS_SECRET_ACCESS_KEY = YOUR_AWS_SECRET_ACCESS_KEY
```

### Download pretrained models from tensorflow's model zoo.

```bash
make download_models
```

Currently, we support single shoot detection with mobilenets and inception.

### Download the inference graph for your model of choice.

#### For mobilenets

```bash
make download_ssd_mobilenets
```

#### For inception

```bash
make download_ssd_inception
```

These make commands will download the respective model and name/replace the current `inference_graph` folder. If you want to switch models, just run the make command again with your model of choice.

### Run the app

```bash
python app.py
```
