from .utils import create_parser
from .update import run_update

if __name__ == '__main__':
    parser = create_parser()
    args = parser.parse_args()
    run_update(args.init_date, args.path)