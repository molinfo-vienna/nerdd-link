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


# def mol_to_svg(
#     mc: Mol,
#     highlights: List[int],
#     molSize=(300, 180),
#     include_atom_indices: bool = False,
# ) -> str:
#     rdDepictor.Compute2DCoords(mc)

#     if include_atom_indices:
#         for a in mc.GetAtoms():
#             a.SetProp("atomLabel", str(a.GetIdx() + 1))
#     else:
#         # remove molAtomMapNumber (to avoid drawing the atom indices)
#         for a in mc.GetAtoms():
#             if a.HasProp("molAtomMapNumber"):
#                 a.ClearProp("molAtomMapNumber")

#     drawer = rdMolDraw2D.MolDraw2DSVG(*molSize)
#     # increase font size of atom labels (default is 12)
#     drawer.drawOptions().minFontSize = 15

#     # highlight soms in orange color and set size of radius to 0.8
#     highlight_atoms = {a: [(255 / 255, 204 / 255, 102 / 255)] for a in highlights}
#     atom_rads = {a: 0.8 for a in highlights}
#     drawer.DrawMoleculeWithHighlights(mc, "", highlight_atoms, {}, atom_rads, {})
#     drawer.FinishDrawing()

#     # remove svg: header for a valid svg
#     svg = drawer.GetDrawingText().replace("svg:", "")
#     svg = re.sub(pattern, "", svg)
#     return svg


class MolSerializer(Serializer):
    def __init__(self, image_size=(300, 180)):
        super().__init__()
        self.image_size = image_size

    def _serialize(self, data):
        return mol_to_svg(data, image_size=self.image_size)

    def type(self):
        return Mol
