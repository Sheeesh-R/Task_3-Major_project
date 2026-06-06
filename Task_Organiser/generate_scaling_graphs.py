import matplotlib.pyplot as plt
import numpy as np
from sklearn.preprocessing import PolynomialFeatures
from sklearn.linear_model import LinearRegression
from sklearn.pipeline import make_pipeline
import os
import logging

# Import our scaling data
from atar_data import SUBJECT_SCALING_POINTS

_LOGGER = logging.getLogger(__name__)


def create_scaling_graph(subject_name: str, output_path: str) -> None:
    """Create a scaling graph for a specific subject.

    Args:
        subject_name: Name of the subject to plot (must be in
            SUBJECT_SCALING_POINTS).
        output_path: File path to save the generated image.
    """

    if subject_name not in SUBJECT_SCALING_POINTS:
        _LOGGER.warning("Subject %s not found in scaling data", subject_name)
        return

    # Get scaling data points
    data_points = SUBJECT_SCALING_POINTS[subject_name]

    # Extract X and y data
    X = np.array([point[0] for point in data_points]).reshape(-1, 1)
    y = np.array([point[1] for point in data_points])

    # Create polynomial regression model (degree 4)
    model = make_pipeline(
        PolynomialFeatures(degree=4, include_bias=False), LinearRegression()
    )

    # Fit the model
    model.fit(X, y)

    # Generate smooth curve for visualization
    X_smooth = np.linspace(min(X.flatten()), max(X.flatten()), 200).reshape(-1, 1)
    y_smooth = model.predict(X_smooth)

    # Create the plot with consistent styling
    plt.figure(figsize=(10, 6), facecolor="white")
    ax = plt.gca()
    ax.set_facecolor("white")

    # Plot original data points with consistent color
    plt.scatter(
        X,
        y,
        color="#dc3545",
        s=80,
        alpha=0.8,
        label="UAC Data Points",
        zorder=5,
        edgecolors="white",
        linewidth=1,
    )

    # Plot polynomial regression curve with consistent color
    plt.plot(
        X_smooth,
        y_smooth,
        color="#007bff",
        linewidth=3,
        label="Polynomial Regression (Degree 4)",
        alpha=0.9,
    )

    # Formatting with consistent fonts and colors
    plt.xlabel("Raw HSC Mark", fontsize=14, fontweight="bold", color="#333333")
    plt.ylabel("Scaled Mark (%)", fontsize=14, fontweight="bold", color="#333333")
    plt.title(
        f"{subject_name} - Scaling Model",
        fontsize=16,
        fontweight="bold",
        pad=20,
        color="#333333",
    )

    # Set axis limits
    plt.xlim(0, 100)
    plt.ylim(0, 100)

    # Grid and styling
    plt.grid(True, alpha=0.2, linestyle="-", color="#cccccc", linewidth=0.5)
    plt.legend(fontsize=11, loc="upper left", frameon=True, fancybox=True, shadow=True)

    # Set tick colors
    ax.tick_params(colors="#666666")

    # Spine styling
    for spine in ax.spines.values():
        spine.set_edgecolor("#dddddd")
        spine.set_linewidth(1)

    plt.tight_layout()

    # Save the graph with consistent settings
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    plt.savefig(
        output_path, dpi=300, bbox_inches="tight", facecolor="white", edgecolor="none"
    )
    plt.close()

    _LOGGER.info("Graph saved: %s", output_path)


def main():
    """Generate scaling graphs for key subjects."""

    # Create graphs directory
    graphs_dir = "static/graphs"
    os.makedirs(graphs_dir, exist_ok=True)

    # Generate graphs for key subjects
    subjects_to_graph = [
        "English Advanced",
        "Mathematics Advanced",
        "Physics",
        "Design & Technology",
    ]

    for subject in subjects_to_graph:
        filename = (
            subject.lower().replace(" ", "_").replace("&", "and") + "_scaling.png"
        )
        output_path = os.path.join(graphs_dir, filename)
        create_scaling_graph(subject, output_path)

    _LOGGER.info("All scaling graphs generated successfully!")


if __name__ == "__main__":
    main()
