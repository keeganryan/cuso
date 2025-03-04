"""Wrapper around flatter's lattice reduction methods"""

from shutil import which
from subprocess import Popen, PIPE
import warnings

from sage.all import Matrix, ZZ

from cuso.exceptions import SolveFailureError
from .lattice_reduction import LatticeReduction


class Flatter(LatticeReduction):
    """Strategy that uses flatter's fast lattice reduction method."""

    def lattice_to_str(self, basis: Matrix) -> str:
        """Convert lattice basis to a string format recognized by flatter.

        Args:
            basis (Matrix): lattice basis

        Returns:
            str: string representation
        """
        row_s = ["[" + " ".join([hex(c) for c in row]) + "]" for row in basis.rows()]
        rep = "[" + "\n".join(row_s) + "\n]\n"
        return rep

    def lattice_from_str(self, basis_s: str) -> Matrix:
        """Convert a string representation to a basis matrix.

        Args:
            basis_s (str): string representation

        Returns:
            Matrix: basis matrix
        """
        rows = basis_s.split("\n")
        if rows[-1] != "" or rows[-2] != "]":
            raise SolveFailureError("Malformed flatter output")
        rows = rows[:-2]
        rows = [row.lstrip("[").rstrip("]") for row in rows]
        rows = [[int(s) for s in row.split(" ")] for row in rows]
        return Matrix(ZZ, rows)

    def reduce_integer_basis(self, basis: Matrix) -> Matrix:
        """Perform lattice basis reduction on an integer matrix.

        Args:
            basis (Matrix): input basis

        Returns:
            Matrix: reduced basis
        """
        if which("flatter") is None:
            warnings.warn(
                "flatter is not installed, using Sage instead. "
                "Please install https://github.com/keeganryan/flatter for faster lattice reduction",
                UserWarning
            )
            return basis.LLL()

        lat_s = self.lattice_to_str(basis)

        proc = Popen("flatter", stdin=PIPE, stdout=PIPE)
        outs, _ = proc.communicate(lat_s.encode())
        if proc.returncode != 0:
            raise SolveFailureError("flatter has nonzero return code")
        red_basis = self.lattice_from_str(outs.decode())
        self.logger.info("Reduced lattice basis using flatter")
        return red_basis
