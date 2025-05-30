import argparse
import asyncio
import time

import torch

from dlslime.remote_io.engine import TransferEngine

parser = argparse.ArgumentParser('sender')


async def main(args):
    test_shape = args.shape
    recv_indices = args.indices
    test_tensor = torch.zeros(test_shape, device='cuda', dtype=torch.bfloat16)

    engine = TransferEngine(args.device, ib_port=1)
    session_id = 0
    buffer_shape = [len(recv_indices)] + test_shape[1:]
    buffer_tensor = torch.zeros(buffer_shape, device=test_tensor.device, dtype=test_tensor.dtype)
    engine.init_link(session_id, buffer_tensor, args.remote_host, args.remote_port, args.port)

    start_time = time.time()
    await engine.buffered_receive_tensor(session_id, test_tensor, recv_indices)
    end_time = time.time()

    duration = end_time - start_time

    num_elem = 1
    for s in buffer_shape:
        num_elem *= s
    total_data_bytes = num_elem * test_tensor.itemsize  # float32 (4 bytes) is the test dtype
    total_data_gb = total_data_bytes / (1e9)
    bandwidth = (total_data_gb) / (duration)
    print(f'Total data size = {total_data_gb} GB, total time = {duration} s, {bandwidth=} GB/s')

    print(torch.sum(buffer_tensor))
    # print(f"{test_tensor=}")
    # print(f"{buffer_tensor=}")
    engine.stop_link(session_id)


if __name__ == '__main__':
    parser.add_argument('--device', type=str, default='mlx5_bond_1')
    parser.add_argument('--port', type=int, default=4433)
    parser.add_argument('--remote-host', type=str, default='localhost')
    parser.add_argument('--remote-port', type=str, default=3344)
    parser.add_argument('--shape', type=int, nargs='+', default=[15000, 64, 1, 128])
    parser.add_argument('--indices', type=int, nargs='+', default=list(range(80)))
    parser.add_argument('--mode', type=str, choices=['batch-send', 'send'], default='batch-send')
    args = parser.parse_args()
    asyncio.run(main(args))
