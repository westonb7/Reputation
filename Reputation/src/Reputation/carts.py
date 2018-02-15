import msgpack
import falcon

## I used this for testing things while following the Falcon tutorial.

class Resource_c(object):
	## Sample request: http localhost:8000/favorites?name="1234"
 
	def on_get(self, req, resp):
		print ("test")
		print (req.get_param('name'))

		myVal = req.get_param('name')

		doc = {
			'carts': [ 'hello' ]
		}

		resp.data = msgpack.packb(doc, use_bin_type=True)
		resp.content_type = falcon.MEDIA_MSGPACK
		resp.status = falcon.HTTP_200

