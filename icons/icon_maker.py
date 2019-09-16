from PIL import Image


colorImage  = Image.open("p1.png")


for theta in range(0, 365, 10):
	rotated = colorImage.rotate(-theta, expand=False)
	rotated = rotated.resize((50, 50), Image.ANTIALIAS)
	outfile = 'p' + str(theta) + '.png'
	rotated.save(outfile, optimize=True, quality=10)

