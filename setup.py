from setuptools import setup
from setuptools import find_packages

REQUIRED_PACKAGES = [
    "apsw==3.9.2.post1",
    "cachetools==3.0.0",
    "deprecated==1.2.7",
    "Flask==1.0.2",
    "gmpy2==2.0.8",
    "kazoo==2.6.1",
    "lmdb==0.94",
    "matplotlib==3.0.2",
    "numba==0.40.1",
    "numpy==1.18.4",
    "pandas==0.23.4",
    "peewee==3.9.3",
    "psutil==5.6.6",
    "pycryptodomex==3.6.6",
    "python-dotenv==0.13.0",
    "redis==3.0.1",
    "requests==2.23.0",
    "ruamel.yaml",
    "scikit-learn==0.19.2",
    "scipy==1.1.0",
    "six==1.14.0",
    "sklearn==0.0",
    "tensorflow==1.15.2",
    "torch==1.4.0",
    "torchvision==0.5.0",
    "tornado==6.0.4",
    "Werkzeug==0.15.3"
]

setup(
    name="FATE",
    version="1.4.0",
    description="An Industrial Level Federated Learning Framework",
    long_description="FATE (Federated AI Technology Enabler) is an open-source project "
                     "initiated by Webank's AI Department to provide a secure computing framework "
                     "to support the federated AI ecosystem. "
                     "It implements secure computation protocols based on homomorphic encryption "
                     "and multi-party computation (MPC). "
                     "It supports federated learning architectures "
                     "and secure computation of various machine learning algorithms, "
                     "including logistic regression, tree-based algorithms, deep learning and transfer learning.",
    license="Apache 2.0",
    url="https://github.com/FederatedAI/FATE",
    author="FATE authors",
    author_email="contact@FedAI.org",
    maintainer="Sage Wei",
    maintainer_email="wbwmat@gmail.com",
    packages=find_packages(".", include=["federatedml*", "arch*", "fate_flow*"]),
    include_package_data=True,
    install_requires=REQUIRED_PACKAGES,
    package_data={
        '': ["*"]
    },
    scripts=['fate_flow/fate_flow_server.py', 'fate_flow/fate_flow_client.py'],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'Intended Audience :: Education',
        'Topic :: Scientific/Engineering',
        'Topic :: Scientific/Engineering :: Mathematics',
        'Topic :: Scientific/Engineering :: Artificial Intelligence',
        'Topic :: Software Development',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7'
    ]
)
