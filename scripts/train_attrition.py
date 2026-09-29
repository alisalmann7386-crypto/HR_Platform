import _bootstrap
import argparse
from src.attrition.training import train
from src.utils.config import IBM
if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--data',default=str(IBM));args=parser.parse_args()
    from scripts.run_eda import run_eda
    run_eda(args.data)
    train(args.data)
