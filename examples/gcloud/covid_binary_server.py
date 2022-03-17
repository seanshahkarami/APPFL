import sys
import time
import logging
import argparse
import json
import torch

from appfl.misc.data import *
from appfl.config import *

import appfl.run_grpc_server as grpc_server


def main():
    # read default configuration
    cfg = OmegaConf.structured(Config)

    parser = argparse.ArgumentParser(description="Provide the configuration")

    parser.add_argument("--nclients", type=int, required=True)
    parser.add_argument("--num_epochs", type=int, required=True)
    parser.add_argument("--num_local_epochs", type=int, required=True)
    parser.add_argument("--lr", type=float, required=True)
    parser.add_argument("--check_intv", type=int, required=True)

    parser.add_argument("--logging", type=str, default="INFO")
    args = parser.parse_args()

    cfg.num_epochs = args.num_epochs
    cfg.fed.args.num_local_epochs = args.num_local_epochs
    cfg.fed.args.optim_args.lr = args.lr

    logging.basicConfig(stream=sys.stdout, level=eval("logging." + args.logging))

    start_time = time.time()

    """ Isabelle's DenseNet (the outputs of the model are probabilities of 1 class ) """
    import importlib.machinery

    loader = importlib.machinery.SourceFileLoader("MainModel", "./IsabelleTorch.py")
    MainModel = loader.load_module()

    file = "./IsabelleTorch.pth"
    model = torch.load(file)
    model.eval()
    cfg.fed.args.loss_type = "torch.nn.BCELoss()"

    logger = logging.getLogger(__name__)
    logger.info(
        f"----------Loaded Data and Model----------Elapsed Time={time.time() - start_time}"
    )
    logger.debug(OmegaConf.to_yaml(cfg))

    """ saving models """
    cfg.save_model = True
    if cfg.save_model == True:
        cfg.save_model_dirname = "./save_models"
        cfg.save_model_filename = "Covid_Binary_Isabelle_FedAvg_LR_%s" % (args.lr)
        cfg.checkpoints_interval = args.check_intv

    grpc_server.run_server(cfg, model, args.nclients)


if __name__ == "__main__":
    main()
