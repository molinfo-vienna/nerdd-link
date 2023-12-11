from .json_encoder import *
from .mol_serializer import *
from .registry import *
from .serializer import *

for serializer in [MolSerializer()]:
    register_serializer(serializer)
