# Model config
INPUT_LAYER_SHAPE = (7, 7, 512)

# Training config
CLASS_ENCODING = {"Maltese dog": 0, "Afghan hound": 1}
ENCODING_CLASS = {0: "Maltese dog", 1: "Afghan hound"}
FNAME_CLASS = {"n02085936": "Maltese dog", "n02088094": "Afghan hound"}
RD_SEED = 1
SPLIT_SEED = 42
TEST_SIZE = 0.5
BATCH_SIZE = 32
EPOCHS = 2
