class Design():

	# General
	main					= {
		'bg'				: '#F0F0F0',
		'font_family'		: 'Arial',
		'font_size'			: 8,

		'floral_white'		: '#fffcf2',
		'silver'			: '#ccc5b9',
		'charcoal_brown'	: '#403d39',
		'carbon_black'		: '#252422',
		'ink_black'			: '#000814',
		'prussian_blue'		: '#001d3d',
		'oxford_navy'		: '#003566',

		'neon_pink'			: '#f72585',
		'raspberry_plum'	: '#b5179e',
		'indigo_bloom'		: '#7209b7',
		'ultrasonice_blue'	: '#560bad',
		'true_azure'		: '#480ca8',
		'vivid_royal'		: '#3a0ca3',
		'persian_blue'		: '#3f37c9',
		'cloud_sky'			: '#4895ef',
		'sky_aqua'			: '#4cc9f0',
	}

	source_dir_tree 		= {
		'main_bg'			: main['ink_black'],
		'hover_bg'			: main['prussian_blue'],
		'select_bg'			: main['oxford_navy'],
	}

	dest_dir_tree 		= {
		'main_bg'			: main['ink_black'],
		'hover_bg'			: main['prussian_blue'],
		'select_bg'			: main['oxford_navy'],
	}

	# Headlines
	headline 				= { 'font_size': 14 },

	# Buttons
	button_general			= { 'padx': 40, 'pady': 10 }

class ConsoleDesign(Design):
	pass

	# # General
	# main					= {
	# 	'bg'				: '#F0F0F0',
	# 	'font_family'		: 'Arial',
	# 	'font_size'			: 8,
	# }

class WindowDesign(Design):
	pass

	# # General
	# main 					= {
	# 	'bg'				: '#F0F0F0',
	# 	'font_family'		: 'Arial',
	# 	'font_size'			: 8,
	# }