#
#  Copyright 2019 The FATE Authors. All Rights Reserved.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
#
from test_example.dsl.stage.base import Stage


class HomoNN(Stage):
    def __init__(self, name=None,
                 config_type="nn",
                 batch_size=-1,
                 optimizer="Adam",
                 learning_rate=0.05,
                 early_stop="diff",
                 eps=1e4,
                 loss="binary_crossentropy",
                 metrics="accuracy",
                 max_iter=10):
        super().__init__(name=name, stage_name="HomoNN")
        self.global_param = dict(
            config_type=config_type,
            batch_size=batch_size,
            optimizer=dict(optimizer=optimizer, learning_rate=learning_rate),
            early_stop=dict(early_stop=early_stop, eps=eps),
            loss=loss,
            metrics=[metrics] if isinstance(metrics, str) else metrics,
            max_iter=max_iter
        )

    def add_layers(self, *layers):
        if "nn_define" not in self.global_param:
            self.global_param["nn_define"] = []
        for layer in layers:
            if isinstance(layer, Layer):
                layer = layer.to_nn()
            self.global_param["nn_define"].append(layer)
        return self


class Layer(object):
    def to_nn(self):
        raise NotImplemented()


class Dense(Layer):
    def __init__(self, units, use_bias=True, activation="sigmoid"):
        self._units = units
        self._use_bias = use_bias
        self._activation = activation

    def to_nn(self):
        return dict(
            layer="Dense",
            units=self._units,
            use_bias=self._use_bias,
            activation=self._activation
        )
