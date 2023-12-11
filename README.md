# NERDD Kafka

Run a [NERDD module](https://github.com/molinfo-vienna/nerdd-module) as a Kafka 
service that consumes input molecules and produces prediction tuples.


## Installation

```bash
pip install -U nerdd-kafka
```
  
## Usage

When a class inherits from ```nerdd_module.AbstractModel``` (see 
[NERDD Module Github page](https://github.com/molinfo-vienna/nerdd-module)), it can be 
used to create a Kafka service. 

```bash 
# run a Kafka service for NerddModel on localhost:9092
run_nerdd_server package.path.to.NerddModel

# modify broker url, input topic and batch size
run_nerdd_server package.path.to.NerddModel \
  --broker-url my-cluster-kafka-bootstrap.kafka:9092 \
  --input-topic examples \
  --batch-size 10

# more information via --help
run_nerdd_server --help
```

If the model class is called ```ExamplePredictionModel```, the server will read input 
tuples from the input topic ```example-prediction-inputs``` in batches of size 100
and write results to the ```results``` topic. The batch size specifies the number
of input tuples that are given to the model at once.