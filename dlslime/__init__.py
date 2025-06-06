from ._slime_c import available_nic
from .assignment import Assignment
from .remote_io.nvlink_endpoint import NVLinkEndpoint
from .remote_io.rdma_endpoint import RDMAEndpoint

__all__ = ['available_nic', 'Assignment', 'NVLinkEndpoint', 'RDMAEndpoint']
