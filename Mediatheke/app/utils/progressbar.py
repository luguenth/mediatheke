import sys
import time

def display_progress_bar(completed, total=None, bar_length=50, interval=0.1, start_time: float|None = None):
    if start_time is None:
        start_time = time.time()
    
    elapsed_time = time.time() - start_time
    # calculate estimated time left
    if completed > 0:
        estimated_time_left = elapsed_time * (total / completed - 1)
    else:
        estimated_time_left = 0

    if total is not None:
        progress = float(completed) / total
        blocks = int(progress * bar_length)
        
        if blocks > 0:
            # Full blocks
            bar = '■' * (blocks - 1)
            # Animated current block with dots
            animated_block = ['.', '..', '...', '…'][int(time.time() // interval % 4)]
            bar += animated_block
        else:
            bar = ''
        
        spaces = ' ' * (bar_length - len(bar))
        
        # also add completed/total
        sys.stdout.write('\r[{0}] {1}% {2} Elapsed: {3}/{4}'.format(bar + spaces, int(round(progress * 100)), f'{completed}/{total}', time.strftime('%H:%M:%S', time.gmtime(elapsed_time)), time.strftime('%H:%M:%S', time.gmtime(estimated_time_left))))
    else:
        sys.stdout.write(f'\r{completed} Elapsed: {time_str}')
        sys.stdout.flush()
