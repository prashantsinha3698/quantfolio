"""
Covariance matrix estimation, eigenvalue checking, and positive semi-definite (PSD) stabilization.
"""
from typing import Tuple
import numpy as np
import pandas as pd
from app.core.config import ANNUALIZATION_FACTOR
from app.core.logging import logger


class CovarianceEstimator:
    """Calculates and regularizes covariance matrices for stable portfolio optimization."""

    @staticmethod
    def sample_covariance(returns_df: pd.DataFrame, annualized: bool = True) -> np.ndarray:
        """Sample covariance matrix using N-1 degrees of freedom."""
        cov = returns_df.cov().values
        if annualized:
            cov = cov * ANNUALIZATION_FACTOR
        return cov

    @staticmethod
    def is_positive_semi_definite(matrix: np.ndarray, tol: float = 1e-8) -> bool:
        """Checks if symmetric matrix has all eigenvalues >= -tol."""
        # Ensure symmetry
        sym_matrix = (matrix + matrix.T) / 2.0
        eigenvalues = np.linalg.eigvalsh(sym_matrix)
        return bool(np.all(eigenvalues >= -tol))

    @staticmethod
    def stabilize_covariance(matrix: np.ndarray, shrinkage_lambda: float = 0.05) -> Tuple[np.ndarray, bool]:
        """
        Ensures covariance matrix is strictly positive semi-definite and well-conditioned.
        If any eigenvalue is <= 0 or condition number is too large, applies diagonal shrinkage:
        Sigma_shrunk = (1 - lambda) * Sigma + lambda * diag(Sigma)
        """
        # Enforce exact symmetry
        sym = (matrix + matrix.T) / 2.0
        eigenvalues, eigenvectors = np.linalg.eigh(sym)

        was_regularized = False
        min_eig = eigenvalues.min()

        if min_eig < 1e-7:
            logger.info(f"Regularizing covariance matrix (min eigenvalue was {min_eig:.2e})")
            was_regularized = True
            # Project onto PSD cone
            clamped_eigs = np.maximum(eigenvalues, 1e-6)
            reconstructed = eigenvectors @ np.diag(clamped_eigs) @ eigenvectors.T
            # Blend with diagonal variance
            diag_var = np.diag(np.diag(reconstructed))
            sym = (1.0 - shrinkage_lambda) * reconstructed + shrinkage_lambda * diag_var

        return sym, was_regularized
