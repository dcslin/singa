#
# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.
#

from singa import autograd, layer, model, tensor, device, opt

class QAModel(model.Model):

    def __init__(self,
                 hidden_size,
                 num_layers=1,
                 bidirectional=True,
                 return_sequences=False):
        super(QAModel, self).__init__()
        self.hidden_size = hidden_size
        self.lstm_q = layer.CudnnRNN(hidden_size=hidden_size,bidirectional=bidirectional,return_sequences=return_sequences)
        self.lstm_a = layer.CudnnRNN(hidden_size=hidden_size,bidirectional=bidirectional,return_sequences=return_sequences)
        self.optimizer = opt.SGD()

    def forward(self, q, a_batch):
        q = self.lstm_q(q)  # bs, Hidden*2
        a_batch = self.lstm_a(a_batch)  # 2bs, Hidden*2

        bs_a = q.shape[0]
        # bs, hid*2
        a_pos, a_neg = autograd.split(a_batch, 0, [bs_a, bs_a])

        sim_pos = autograd.cossim(q, a_pos)
        sim_neg = autograd.cossim(q, a_neg)
        return sim_pos, sim_neg

class QAModel_mean(model.Model):

    def __init__(self,
                 hidden_size,
                 q_seq,
                 a_seq,
                 num_layers=1,
                 bidirectional=False,
                 return_sequences=True):
        super(QAModel_mean, self).__init__()
        self.hidden_size = hidden_size
        self.lstm_q = layer.CudnnRNN(hidden_size=hidden_size,bidirectional=bidirectional,return_sequences=return_sequences)
        self.lstm_a = layer.CudnnRNN(hidden_size=hidden_size,bidirectional=bidirectional,return_sequences=return_sequences)
        # self.q_pool = layer.MaxPool2d((q_seq,1))
        # self.a_pool = layer.MaxPool2d((a_seq,1))
        self.optimizer = opt.SGD(0.01, 0.9)

    def forward(self, q, a_batch):
        q = self.lstm_q(q)  # bs, seq, Hidden*2
        a_batch = self.lstm_a(a_batch)  # 2bs, seq, Hidden*2

        # bs, hid*2
        q=autograd.reduce_mean(q,axes=[1],keepdims=0)

        # autograd.reducemean

        # bs, 1, seq, hid*2
        # q = autograd.reshape(q, (q.shape[0], 1, q.shape[1], q.shape[2]))
        # bs, 1, 1, hid*2
        # q = self.q_pool(q)
        # bs, hid*2
        # q = autograd.reshape(q, (q.shape[0], q.shape[3]))

        # 2bs, 1, seq, hid*2
        # a_batch = autograd.reshape(a_batch, (a_batch.shape[0], 1, a_batch.shape[1], a_batch.shape[2]))
        # 2bs, 1, 1, hid*2
        # a_batch = self.a_pool(a_batch)
        # 2bs, hid*2
        # a_batch = autograd.reshape(a_batch, (a_batch.shape[0], a_batch.shape[3]))

        bs_a = q.shape[0]
        # 2*(bs, seq, hid*2)
        a_pos, a_neg = autograd.split(a_batch, 0, [bs_a, bs_a])
        # 2*(bs, hid*2)
        a_pos=autograd.reduce_mean(a_pos,axes=[1],keepdims=0)
        a_neg=autograd.reduce_mean(a_neg,axes=[1],keepdims=0)

        sim_pos = autograd.cossim(q, a_pos)
        sim_neg = autograd.cossim(q, a_neg)
        return sim_pos, sim_neg



if __name__ == "__main__":
    m = QAModel(2,return_sequences=False)
    dev = device.create_cuda_gpu_on(7)

    tq = tensor.random((2, 3, 4),dev)
    ta = tensor.random((2 * 2, 3, 4),dev)

    m.train()
    for i in range(10):
        out = m.forward(tq, ta)
        loss = autograd.qa_lstm_loss(out[0], out[1])
        m.optimizer(loss)
        print(loss)