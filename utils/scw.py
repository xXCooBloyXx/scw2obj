from utils.reader import Reader

class SCWGeometrySource:
	def __init__(self, read):
		self.semantic = read.readUTF()
		self.indexOffset = read.readUByte()
		self.indexSet = read.readUByte()
		self.stride = read.readUByte()
		self.scale = read.readFloat()
		self.count = read.readInt()
		self.points = []
		for i in range(self.count):
			point = []
			for j in range(self.stride):
				point.append(round(read.readNShort()*self.scale, 6))
			self.points.append(point)

class SCWGeometryMesh:
	def __init__(self, read):
		self.materialSymbol = read.readUTF()
		self.count = read.readInt()
		self.inputsCount = read.readUByte()
		self.indexLength = read.readUByte()
		self.triangles = []
		for i in range(self.count):
			triangle = []
			for j in range(3):
				vertexIndex = []
				for k in range(self.inputsCount):
					vertexIndex.append(read.readUInteger(self.indexLength))
				triangle.append(vertexIndex)
			self.triangles.append(triangle)

class SCWGeometry:
	def __init__(self, read, fileVersion):
		self.name = read.readUTF()
		self.group = read.readUTF()
		if fileVersion <= 1:
			read.stream.skip(64) # unknownMatrix4x4
		self.sourcesCount = read.readUByte()
		self.sources = []
		for i in range(self.sourcesCount):
			source = SCWGeometrySource(read)
			self.sources.append(source)
		self.hasBindShapeMatrix = read.readUByte()
		if self.hasBindShapeMatrix == 1:
			read.stream.skip(64)
		self.jointsCount = read.readUByte()
		for i in range(self.jointsCount):
			read.readUTF()
			read.stream.skip(64)
		self.weightsCount = read.readInt()
		for i in range(self.weightsCount):
			read.stream.skip(4)
			if fileVersion >= 1:
				read.stream.skip(8)
			else:
				read.stream.skip(4)
		self.meshesCount = read.readUByte()
		self.meshes = []
		for i in range(self.meshesCount):
			mesh = SCWGeometryMesh(read)
			self.meshes.append(mesh)

class SCWHeader:
	def __init__(self, read):
		self.fileVersion = read.readUShort()
		self.frameRate = read.readUShort()
		self.frameStart = read.readUShort()
		self.frameEnd = read.readUShort()
		self.materialsFile = read.readUTF()
		if self.fileVersion >= 1:
			self.overrideMaterialsFromFile = read.readUByte()

class SCWFile:
	def __init__(self, filename=""):
		self.filename = filename
		self.header = ""
		self.geometries = []

	def loadScw(self, chunks=None):
		with open(self.filename, "rb") as file:
			data = file.read()
			self.datalen = len(data)
			read = Reader(data)
			read.__init__(data, ">")
			if read.stream.read(4) != b"SC3D":
				print("[ERROR] Incorrect SCW magic!")
			else:
				return self.loadChunks(read, chunks)

	def loadChunks(self, read, chunks=[]):
		while True:
			length = read.readInt()
			chunk = read.stream.read(4)
			offset = read.stream.tell()+length
			if chunk == b"HEAD":
				fileVersion = self.readHeadChunk(read)
			elif chunk == b"GEOM":
				self.readGeomChunk(read)

			crc = read.readInt()
			read.stream.seek(offset+4) # doesnt work?
			if chunk == b"WEND":
				return self.header, self.geometries
				break

	def readHeadChunk(self, read):
		head = SCWHeader(read)
		self.fileVersion = head.fileVersion
		self.header = head

	def readGeomChunk(self, read):
		geom = SCWGeometry(read, self.fileVersion)
		self.geometries.append(geom)