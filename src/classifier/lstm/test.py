if __name__ == '__main__':
    from src.classifier.lstm.lstm import LSTM
    import src.classifier.lstm.util as util
    import time

    start = time.time()
    print str(start), "\tstart "
#     np.set_printoptions(precision=2, threshold=np.nan)
    import properties.config as c
    conf = c.getInstance("../../").getConfig("lstm")
    lstm = LSTM(config=conf, relative="../../")
#     lstm.createPyBrainDatasetFromSamples(True, "dataset")
    lstm.startTraining("datasettest", True)
    print time.time(), "\tload network "
    lstm.net = util.load_network('lstm_dummy')
    print time.time(), "\tstart validate "
    lstm.validate()
    end = time.time()
    print str(end), "\tend "
    print str(end - start), "\tdifftime"
#     NetworkWriter.writeToFile(lstm.net, 'lstm_backprop.xml')

