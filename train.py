import sys
import argparse
import Models , LoadBatches


def parse(argv):

	parser = argparse.ArgumentParser()
	parser.add_argument("--save_weights_path", type = str  )
	parser.add_argument("--train_images", type = str  )
	parser.add_argument("--train_annotations", type = str  )
	parser.add_argument("--n_classes", type=int )
	parser.add_argument("--input_height", type=int , default = 224  )
	parser.add_argument("--input_width", type=int , default = 224 )

	parser.add_argument('--validate',action='store_false')
	parser.add_argument("--val_images", type = str , default = "")
	parser.add_argument("--val_annotations", type = str , default = "")

	parser.add_argument("--epochs", type = int, default = 5 )
	parser.add_argument("--batch_size", type = int, default = 2 )
	parser.add_argument("--val_batch_size", type = int, default = 2 )
	parser.add_argument("--load_weights", type = str , default = "")

	parser.add_argument("--model_name", type = str , default = "")
	parser.add_argument("--optimizer_name", type = str , default = "adadelta")


	return parser.parse_args(argv)

def train(args):

	train_images_path = args.train_images
	train_segs_path = args.train_annotations
	train_batch_size = args.batch_size
	val_batch_size = args.val_batch_size
	n_classes = args.n_classes
	input_height = args.input_height
	input_width = args.input_width
	validate = args.validate
	save_weights_path = args.save_weights_path
	epochs = args.epochs

	load_weights = args.load_weights

	optimizer_name = args.optimizer_name
	model_name = args.model_name

	if validate:
		val_images_path = args.val_images
		val_segs_path = args.val_annotations
		val_batch_size = args.val_batch_size

	modelFns = { 'vgg_segnet':Models.VGGSegnet.VGGSegnet , 'vgg_unet':Models.VGGUnet.VGGUnet , 'vgg_unet2':Models.VGGUnet.VGGUnet2 , 'fcn8':Models.FCN8.FCN8 , 'fcn32':Models.FCN32.FCN32   }
	modelFN = modelFns[ model_name ]

	m = modelFN( n_classes , input_height=input_height, input_width=input_width)
	m.compile(loss='categorical_crossentropy',
	      optimizer= optimizer_name ,
	      metrics=['accuracy'])


	if len( load_weights ) > 0:
		m.load_weights(load_weights)


	print("Model output shape" ,  m.output_shape)

	output_height = m.outputHeight
	output_width = m.outputWidth

	G  = LoadBatches.imageSegmentationGenerator( train_images_path , train_segs_path ,  train_batch_size,  n_classes , input_height , input_width , output_height , output_width   )


	if validate:
		G2  = LoadBatches.imageSegmentationGenerator( val_images_path , val_segs_path ,  val_batch_size,  n_classes , input_height , input_width , output_height , output_width   )

	n_train_images = 367  # hardcoded n images in training dataset
	n_val_images = 101  # hardcoded n images in validation dataset
	
	if not validate:
		for ep in range( epochs ):
			print("Epoch %d / %d\n" % (ep+1, epochs))
			m.fit_generator( G , int(n_train_images/train_batch_size)  , epochs=1 )
			m.save_weights( save_weights_path + "." + str( ep ) )
			m.save( save_weights_path + ".model." + str( ep ) )
	else:
		for ep in range( epochs ):
			print("Epoch %d / %d\n" % (ep+1, epochs))
			m.fit_generator( G , int(n_train_images/train_batch_size)  , validation_data=G2 , validation_steps=int(n_val_images/val_batch_size) ,  epochs=1 )
			m.save_weights( save_weights_path + "." + str( ep )  )
			m.save( save_weights_path + ".model." + str( ep ) )


if __name__ == '__main__':

	argv = sys.argv
	args = parse(argv[1:])

	train(args)