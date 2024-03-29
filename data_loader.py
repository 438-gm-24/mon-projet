import tensorflow as tf

from . import cyclegan_datasets
from . import model


def _load_samples(csv_name, image_type):
    filename_queue = tf.train.string_input_producer(
        [csv_name])

    reader = tf.TextLineReader()
    _, csv_filename = reader.read(filename_queue)

    record_defaults = [tf.constant([], dtype=tf.string),
                       tf.constant([], dtype=tf.string)]

    filename_i, filename_j = tf.decode_csv(
        csv_filename, record_defaults=record_defaults)

    file_contents_i = tf.read_file(filename_i)
    file_contents_j = tf.read_file(filename_j)
    if image_type == '.jpg':
        image_decoded_A = tf.image.decode_jpeg(
            file_contents_i, channels=model.IMG_CHANNELS)
        image_decoded_B = tf.image.decode_jpeg(
            file_contents_j, channels=model.IMG_CHANNELS)
    elif image_type == '.png':
        image_decoded_A = tf.image.decode_png(
            file_contents_i, channels=model.IMG_CHANNELS, dtype=tf.uint8)
        image_decoded_B = tf.image.decode_png(
            file_contents_j, channels=model.IMG_CHANNELS, dtype=tf.uint8)

    return image_decoded_A, image_decoded_B


def load_data(dataset_name, image_size_before_crop,
              do_shuffle=True, do_flipping=False):
   
    if dataset_name not in cyclegan_datasets.DATASET_TO_SIZES:
        raise ValueError('split name %s was not recognized.'
                         % dataset_name)

    csv_name = cyclegan_datasets.PATH_TO_CSV[dataset_name]

    image_i, image_j = _load_samples(
        csv_name, cyclegan_datasets.DATASET_TO_IMAGETYPE[dataset_name])

    # Preprocessing:
    image_i = tf.image.resize_images(
        image_i, [image_size_before_crop, image_size_before_crop])
    image_j = tf.image.resize_images(
        image_j, [image_size_before_crop, image_size_before_crop])

    if do_flipping is True:
        image_i = tf.image.random_flip_left_right(image_i)
        image_j = tf.image.random_flip_left_right(image_j)

    image_i = tf.random_crop(
        image_i, [model.IMG_HEIGHT, model.IMG_WIDTH, 3])
    image_j = tf.random_crop(
        image_j, [model.IMG_HEIGHT, model.IMG_WIDTH, 3])

    image_i = tf.subtract(tf.div(image_i, 127.5), 1)
    image_j = tf.subtract(tf.div(image_j, 127.5), 1)

    # Batch
    if do_shuffle is True:
        images_i, images_j = tf.train.shuffle_batch(
            [image_i, image_j], 1, 5000, 100)
    else:
        images_i, images_j = tf.train.batch(
            [image_i, image_j], 1)

    inputs = {
        'images_i': images_i,
        'images_j': images_j
    }

    return inputs
