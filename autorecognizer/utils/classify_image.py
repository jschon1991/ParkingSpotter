import numpy as np
# noinspection PyPackageRequirements
import tensorflow as tf
import os

PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))


# noinspection PyPep8Naming
def create_graph(modelFullPath):
    """Creates a graph from saved GraphDef file and returns a saver."""
    # Creates graph from saved graph_def.pb.
    with tf.gfile.FastGFile(modelFullPath, 'rb') as f:
        graph_def = tf.GraphDef()
        graph_def.ParseFromString(f.read())
        _ = tf.import_graph_def(graph_def, name='')


def classify(data, graph):
    run_inference_on_data(data, graph)


def run_inference_on_data(data, graph):
    create_graph(graph.path)
    for dataitem in data:
        answer = ''

        if not tf.gfile.Exists(dataitem['img']):
            tf.logging.fatal('File does not exist %s', dataitem['img'])
            return answer

        image_data = tf.gfile.FastGFile(dataitem['img'], 'rb').read()

        with tf.Session() as sess:

            softmax_tensor = sess.graph.get_tensor_by_name('final_result:0')
            predictions = sess.run(softmax_tensor, {'DecodeJpeg/contents:0': image_data})
            predictions = np.squeeze(predictions)

            top_k = predictions.argsort()[-5:][::-1]  # Getting top 5 predictions
            f = open(graph.labelsPath, 'rb')
            lines = f.readlines()
            labels = [str(w).replace("\n", "") for w in lines]
            print(dataitem['img'] + ' - ' + labels[top_k[0]])
            dataitem['spot'].status = labels[top_k[0]]
            dataitem['spot'].status = dataitem['spot'].status[2:(len(dataitem['spot'].status)-3)]
            dataitem['spot'].save()
