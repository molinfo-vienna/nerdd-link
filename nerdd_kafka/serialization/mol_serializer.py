import re

from rdkit.Chem import Kekulize, Mol, rdDepictor
from rdkit.Chem.Draw import rdMolDraw2D

from .serializer import Serializer

__all__ = ["MolSerializer"]

pattern = re.compile(r"<\?xml.*\?>")


def mol_to_svg(mol: Mol, image_size=(300, 180)) -> str:
    mc = Mol(mol)
    try:
        Kekulize(mc)
    except:
        mc = Mol(mol)

    if mc.GetNumConformers() == 0:
        rdDepictor.Compute2DCoords(mc)

    # remove molAtomMapNumber (to avoid atom indices to be drawn)
    for a in mc.GetAtoms():
        if a.HasProp("molAtomMapNumber"):
            a.ClearProp("molAtomMapNumber")

    drawer = rdMolDraw2D.MolDraw2DSVG(*image_size)
    drawer.DrawMolecule(mc)
    drawer.FinishDrawing()
    svg = drawer.GetDrawingText().replace("svg:", "")
    svg = re.sub(pattern, "", svg)
    return svg


class MolSerializer(Serializer):
    def __init__(self, image_size=(300, 180)):
        super().__init__()
        self.image_size = image_size

    def _serialize(self, data):
        return mol_to_svg(data, image_size=self.image_size)

    def type(self):
        return Mol