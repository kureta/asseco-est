import setuptools

setuptools.setup(
    name="asseco-est", # Replace with your own username
    version="0.0.1",
    author="Sahin Kureta",
    author_email="skureta@gmail.com",
    description="Credit card plugin for Saleor backend",
    url="https://github.com/kureta/asseco-est",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    entry_points={
        "saleor.plugins": [
            "asseco_est = asseco_est.plugin:AssecoEST"
        ]
    }
)
