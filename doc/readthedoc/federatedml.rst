Federated Machine Learning
==========================

FederatedML includes implementation of many common machine learning algorithms on federated learning. All modules are developed in a decoupling modular approach to enhance scalability. Specifically, we provide:

1. Federated Statistic: PSI, Union, Pearson Correlation, etc.

2. Federated Feature Engineering: Feature Sampling, Feature Binning, Feature Selection, etc.

3. Federated Machine Learning Algorithms: LR, GBDT, DNN, TransferLearning, which support Heterogeneous and Homogeneous styles.

4. Model Evaluation: Binary|Multiclass|Regression Evaluation, Local vs Federated Comparison.

5. Secure Protocol: Provides multiple security protocols for secure multi-party computing and interaction between participants.

.. image:: ../../doc/images/federatedml_structure.png
   :width: 800
   :alt: federatedml structure

Algorithm List
--------------

DataIO
^^^^^^

This component is typically the first component of a modeling task. It will transform user-uploaded date into Instance object which can be used for the following components.

- Corresponding module name: DataIO

- Data Input: DTable, values are raw data.
- Data Output: Transformed DTable, values are data instance define in federatedml/feature/instance.py

Param
~~~~~~

.. autoclass:: federatedml.param.dataio_param.DataIOParam
   :members:
   :show-inheritance:

Detail
~~~~~~

.. include:: dataio.rst
   :start-after: .. include_after_this_label