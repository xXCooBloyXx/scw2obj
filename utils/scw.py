from .reader import Reader

class SCWMaterial:
	def __init__(self, read, fileVersion):
		self.name = read.readUTF()
		self.shaderFile = read.readUTF()
		self.blendMode = read.readUByte()
		self.unknownByte = read.readUByte()
		self.ambient = read.readARGB()
		self.diffuse = read.readUniform()
		self.specular = read.readUniform()
		self.stencilTex2D = read.readUTF()
		if fileVersion >= 1:
			self.normalTex2D = read.readUTF()
		self.colorize = read.readUniform()
		self.emission = read.readUniform()
		self.opacityTex2D = read.readUTF()
		self.opacity = read.readFloat()
		self.unknownFloat = read.readFloat()
		self.lightmapDiffuseTex2D = read.readUTF()
		self.lightmapSpecularTex2D = read.readUTF()
		if fileVersion >= 2:
			self.lightmapBackedTex2D = read.readUTF()
		self.shaderDefineFlags = read.readInt()
		if bool(self.shaderDefineFlags & 0x8000):
			self.clipPlane = [read.readFloat(), read.readFloat(), read.readFloat(), read.readFloat()]

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

class SCWGeometryVertexWeight:
	def __init__(self, read, fileVersion):
		self.jointIds = [read.readUByte(), read.readUByte(), read.readUByte(), read.readUByte()]
		if fileVersion >= 1:
			self.weights = [read.readNUShort(), read.readNUShort(), read.readNUShort(), read.readNUShort()]
		else:
			self.weights = [read.readNUByte(), read.readNUByte(), read.readNUByte(), read.readNUByte()]

class SCWGeometryJoint:
	def __init__(self, read):
		self.name = read.readUTF()
		self.matrix = read.readMatrix4x4()

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

class SCWGeometry:
	def __init__(self, read, fileVersion):
		self.name = read.readUTF()
		self.groupName = read.readUTF()
		if fileVersion <= 1:
			self.hasUnusedMatrix = 1
			self.unusedMatrix = read.readMatrix4x4()
		else:
			self.hasUnusedMatrix = 0
		self.sourcesCount = read.readUByte()
		self.sources = []
		for i in range(self.sourcesCount):
			source = SCWGeometrySource(read)
			self.sources.append(source)
		self.hasBindShapeMatrix = read.readUByte()
		if self.hasBindShapeMatrix == 1:
			self.bindShapeMatrix = read.readMatrix4x4()
		self.jointsCount = read.readUByte()
		self.joints = []
		for i in range(self.jointsCount):
			joint = SCWGeometryJoint(read)
			self.joints.append(joint)
		self.vertexWeightsCount = read.readInt()
		self.vertexWeights = []
		for i in range(self.vertexWeightsCount):
			vertexWeight = SCWGeometryVertexWeight(read, fileVersion)
			self.vertexWeights.append(vertexWeight)
		self.meshesCount = read.readUByte()
		self.meshes = []
		for i in range(self.meshesCount):
			mesh = SCWGeometryMesh(read)
			self.meshes.append(mesh)

class SCWCamera:
	def __init__(self, read):
		self.name = read.readUTF()
		self.yFov = read.readFloat()
		self.xFov = read.readFloat()
		self.aspectRatio = read.readFloat()
		self.zNear = read.readFloat()
		self.zFar = read.readFloat()

class SCWHeader:
	def __init__(self, read, scwfixver):
		if scwfixver == "0.5":
			self.fileVersion = read.readUShort()
			self.fileVersion = 1
		else:
			self.fileVersion = read.readUShort()
		self.frameRate = read.readUShort()
		self.frameStart = read.readUShort()
		self.frameEnd = read.readUShort()
		self.materialsFile = read.readUTF()
		if self.fileVersion >= 1:
			if scwfixver != "0.5":
				self.overrideMaterialsFromFile = read.readUByte()

class SCWNodeNodeInstanceMaterial:
	def __init__(self, read):
		self.symbol = read.readUTF()
		self.target = read.readUTF()

class SCWNodeNodeInstance:
	def __init__(self, read):
		self.type = read.stream.read(4).decode("UTF-8")
		if self.type in ["CONT", "GEOM"]:
			self.targetInstance = read.readUTF()
			self.materialsCount = read.readUShort()
			self.materials = []
			for i in range(self.materialsCount):
				material = SCWNodeNodeInstanceMaterial(read)
				self.materials.append(material)
		elif self.type == "CAME":
			self.targetInstance = read.readUTF()
			self.lookAtTarget = read.readUTF()

class SCWNodeNodeFrame:
	def __init__(self, read, flags, frames):
		self.id = read.readUShort()
		self.rotation = {}
		self.position = {}
		self.scale = {}
		if flags & 1 != 0:
			self.rotation["x"] = read.readNShort()
			self.rotation["y"] = read.readNShort()
			self.rotation["z"] = read.readNShort()
			self.rotation["w"] = read.readNShort()
		else:
			self.rotation = frames[0].rotation
		if flags & 2 != 0:
			self.position["x"] = read.readFloat()
		else:
			self.position["x"] = frames[0].position["x"]
		if flags & 4 != 0:
			self.position["y"] = read.readFloat()
		else:
			self.position["y"] = frames[0].position["y"]
		if flags & 8 != 0:
			self.position["z"] = read.readFloat()
		else:
			self.position["z"] = frames[0].position["z"]
		if flags & 16 != 0:
			self.scale["x"] = read.readFloat()
		else:
			self.scale["x"] = frames[0].scale["x"]
		if flags & 32 != 0:
			self.scale["y"] = read.readFloat()
		else:
			self.scale["y"] = frames[0].scale["y"]
		if flags & 64 != 0:
			self.scale["z"] = read.readFloat()
		else:
			self.scale["z"] = frames[0].scale["z"]

class SCWNodeNode:
	def __init__(self, read, fileVersion, scwfixver):
		self.name = read.readUTF()
		self.parentName = read.readUTF()
		self.instancesCount = read.readUShort()
		self.instances = []
		for i in range(self.instancesCount):
			instance = SCWNodeNodeInstance(read)
			self.instances.append(instance)
		if fileVersion == 0:
			if scwfixver == "0.25":
				self.framesCount = read.readUShort()
			else:
				self.framesCount = read.readUInt()
		else:
			self.framesCount = read.readUShort()
		self.frames = []
		if self.framesCount != 0:
			if fileVersion == 0:
				if scwfixver == "0.25":
					self.frameFlags = read.readUByte()
				else:
					self.frameFlags = 127
			else:
				self.frameFlags = read.readUByte()
		for i in range(self.framesCount):
			if i == 0:
				flags = 127
			else:
				flags = self.frameFlags
			frame = SCWNodeNodeFrame(read, flags, self.frames)
			self.frames.append(frame)

class SCWNode:
	def __init__(self, read, fileVersion, scwfixver):
		self.nodesCount = read.readUShort()
		self.nodes = []
		for i in range(self.nodesCount):
			node = SCWNodeNode(read, fileVersion, scwfixver)
			self.nodes.append(node)

class SCWFile:
	def __init__(self, filename=""):
		self.filename = filename
		self.header = ""
		self.node = ""
		self.materials = []
		self.geometries = []
		self.cameras = []

	def loadScw(self, scwfixver=None, chunks=None):
		with open(self.filename, "rb") as file:
			data = file.read()
			read = Reader(data, ">")
			if read.readChar(4) != "SC3D":
				print("[ERROR] Incorrect SCW magic!")
			else:
				return self.loadChunks(read, scwfixver, chunks)

	def loadChunks(self, read, scwfixver, chunks=[]):
		while True:
			length = read.readInt()
			chunk = read.readChar(4)
			offset = read.stream.tell()+length
			if chunks != None:
				if chunk == "HEAD":
					fileVersion = self.readHeadChunk(read, scwfixver)
				else:
					if chunk in chunks:
						if chunk == "MATE":
							self.readMateChunk(read)
						elif chunk == "GEOM":
							self.readGeomChunk(read)
						elif chunk == "NODE":
							self.readNodeChunk(read, scwfixver)
						elif chunk == "CAME":
							self.readCameChunk(read)
			else:
				if chunk == "HEAD":
					fileVersion = self.readHeadChunk(read, scwfixver)
				elif chunk == "MATE":
					self.readMateChunk(read)
				elif chunk == "GEOM":
					self.readGeomChunk(read)
				elif chunk == "NODE":
					self.readNodeChunk(read, scwfixver)
				elif chunk == "CAME":
					self.readCameChunk(read)

			if chunks != None:
				read.stream.seek(offset)
			crc = read.readInt()
			if chunk == "WEND":
				return self.header, self.materials, self.geometries, self.cameras, self.node
				break

	def readHeadChunk(self, read, scwfixver):
		head = SCWHeader(read, scwfixver)
		self.fileVersion = head.fileVersion
		self.header = head

	def readMateChunk(self, read):
		mate = SCWMaterial(read, self.fileVersion)
		self.materials.append(mate)

	def readGeomChunk(self, read):
		geom = SCWGeometry(read, self.fileVersion)
		self.geometries.append(geom)

	def readNodeChunk(self, read, scwfixver):
		node = SCWNode(read, self.fileVersion, scwfixver)
		self.node = node

	def readCameChunk(self, read):
		came = SCWCamera(read)
		self.cameras.append(came)