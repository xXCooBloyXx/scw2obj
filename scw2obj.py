from utils.scw import *
import os

for folder in ["scw", "obj"]:
	if not os.path.exists(folder):
		os.makedirs(folder)

def scw2obj(filename, outfile):
	header, geometries = SCWFile(filename).loadScw()
	if len(geometries) == 0:
		print(f"No geometries found in file {os.path.basename(filename)} skipping...")
		return
	else:
		print(f"Converting {os.path.basename(filename)}...")
	obj = open(outfile, "w")
	obj.write("#File Generated using xXCooBloyXx's scw2obj tool\n\n")
	gv = 0
	gn = 0
	gt = 0
	for geom in geometries:
		facevertexindex = None
		facenormalindex = None
		facetexcoordindex = None
		print(f"Writing mesh {geom.name}...")
		obj.write(f"o {geom.name}\n")
		for source in geom.sources:
			if source.semantic in ["VERTEX", "POSITION"]:
				facevertexindex = source.indexOffset
				for verts in source.points:
					obj.write(f"v {verts[0]} {verts[1]} {verts[2]}\n")
				tgv = len(source.points)
			elif source.semantic == "NORMAL":
				facenormalindex = source.indexOffset
				for norms in source.points:
					obj.write(f"vn {norms[0]} {norms[1]} {norms[2]}\n")
				tgn = len(source.points)
			elif source.semantic == "TEXCOORD":
				facetexcoordindex = source.indexOffset
				for texs in source.points:
					obj.write(f"vt {texs[0]} {1-texs[1]}\n")
				tgt = len(source.points)
		for mesh in geom.meshes:
			obj.write(f"usemtl {mesh.materialSymbol}\n")
			for face in mesh.triangles:
				if facenormalindex == None:
					facenormalindex = facevertexindex
				value = f"{face[0][facevertexindex]+1+gv}/{face[0][facetexcoordindex]+1+gt}/{face[0][facenormalindex]+1+gn} {face[1][facevertexindex]+1+gv}/{face[1][facetexcoordindex]+1+gt}/{face[1][facenormalindex]+1+gn} {face[2][facevertexindex]+1+gv}/{face[2][facetexcoordindex]+1+gt}/{face[2][facenormalindex]+1+gn}"
				obj.write(f"f {value}\n")
		gv += tgv
		gn += tgn
		gt += tgt

errors = open("errors.txt", "w")
for filename in os.listdir("./scw"):
	if filename.endswith(".scw"):
		try:
			scw2obj(f"./scw/{filename}", f"./obj/{os.path.basename(filename)[:-4]}.obj")
		except Exception as e:
			print(f"Failed to convert {filename} skipping... Error: {e}")
			errors.write(f"Error while converting {filename}: {e}\n")
			pass
errors.close()
print("Done")
os.system("pause")