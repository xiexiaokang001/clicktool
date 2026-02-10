import sys
import os
import logging
import argparse
import time
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from src.config import Config
from src.ocr import ScreenOCR
from src.clicker import Clicker
from src.scheduler import TaskScheduler


def setup_logging(level: str = 'INFO'):
    log_format = '%(asctime)s - %(levelname)s - %(message)s'
    logging.basicConfig(level=getattr(logging, level), format=log_format)
    return logging.getLogger(__name__)


def run_click_task(config: Config, target_text: str, logger):
    ocr = ScreenOCR(config)
    clicker = Clicker(config)

    logger.info(f"正在查找文字: {target_text}")

    position = ocr.get_text_position(target_text)
    if position:
        x, y = position
        logger.info(f"找到目标位置: ({x}, {y})")
        clicker.click(x, y)
        logger.info(f"点击完成")
        return True
    else:
        logger.warning(f"未找到文字: {target_text}")
        return False


def run_quantity_task(config: Config, target_text: str, logger):
    quantity_config = config.quantity
    total_clicks = quantity_config.get('total_clicks', 100)
    clicks_per_round = quantity_config.get('clicks_per_round', 10)
    round_interval = quantity_config.get('round_interval', 5.0)

    logger.info(f"开始定量点击任务: 总计{total_clicks}次, 每轮{clicks_per_round}次")

    completed = 0
    while completed < total_clicks:
        clicks_in_round = min(clicks_per_round, total_clicks - completed)
        for i in range(clicks_in_round):
            if run_click_task(config, target_text, logger):
                completed += 1
                logger.info(f"进度: {completed}/{total_clicks}")
            else:
                logger.warning(f"点击失败，跳过本次")
        if completed < total_clicks:
            time.sleep(round_interval)

    logger.info("定量点击任务完成")


def main():
    parser = argparse.ArgumentParser(description='屏幕文字识别自动点击工具')
    parser.add_argument('-t', '--text', type=str, help='要识别和点击的目标文字')
    parser.add_argument('-s', '--sequence', type=str,
                        help='多个目标序列，用逗号分隔，如: 帮助,关于')
    parser.add_argument('-c', '--config', type=str, default='config.yaml',
                        help='配置文件路径')
    parser.add_argument('-n', '--number', type=int, default=1,
                        help='点击次数，默认1次')
    parser.add_argument('-i', '--interval', type=float, default=2.0,
                        help='每次点击之间的间隔（秒），默认2秒')
    parser.add_argument('--quantity', action='store_true',
                        help='启用定量点击模式')
    parser.add_argument('--schedule', action='store_true',
                        help='启用定时任务模式')
    parser.add_argument('--list-text', action='store_true',
                        help='识别并列出屏幕上所有文字')

    args = parser.parse_args()

    logger = setup_logging()
    config = Config(args.config)

    if args.list_text:
        ocr = ScreenOCR(config)
        all_text = ocr.recognize_all_text()
        print("\n=== 屏幕上识别到的文字 ===")
        print(all_text)
        return

    if not args.text and not args.sequence:
        parser.print_help()
        print("\n请使用 -t 参数指定要点击的文字，或使用 -s 参数指定多个目标")
        return

    if args.quantity:
        run_quantity_task(config, args.text, logger)
    elif args.schedule:
        scheduler = TaskScheduler(config)
        scheduler.start(run_click_task, config, args.text, logger)
    elif args.sequence:
        targets = [t.strip() for t in args.sequence.split(',')]
        logger.info(f"开始序列点击任务，目标: {targets}")
        for i, target in enumerate(targets):
            for j in range(args.number):
                if i > 0 or j > 0:
                    logger.info(f"等待 {args.interval} 秒...")
                    time.sleep(args.interval)
                run_click_task(config, target, logger)
            logger.info(f"完成目标 {i+1}/{len(targets)}: {target}")
        logger.info("所有任务完成")
    else:
        for i in range(args.number):
            if i > 0:
                logger.info(f"等待 {args.interval} 秒后进行第 {i+1} 次点击...")
                time.sleep(args.interval)
            run_click_task(config, args.text, logger)
        logger.info(f"任务完成，共点击 {args.number} 次")


if __name__ == '__main__':
    main()
