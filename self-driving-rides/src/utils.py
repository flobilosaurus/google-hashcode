import sys

def read_input(instance, parse_function):
    f = open('../input/' + instance + '.in', 'r')
    content = f.readlines()
    f.close()
    return parse_function(content)


def write_output(instance, lines):
    f = open('../output/' + instance + '.out', 'w')
    for line in lines:
        f.write(line+'\n')
    f.close()


class ProgressPrinter():
    def __init__(self, total):
        self.total = total
        self.last_score = None
        self.bar_length = 50

        self.OKGREEN = '\033[92m'
        self.ENDC = '\033[0m'

    def print(self, count, current_score):
        if count % (self.total // min(self.total, 10)) == 0:
            filled_len = self.get_filled_length(count)
            percents = self.get_percents(count)
            bar = self.get_bar(filled_len)

            score_string = self.get_score_string(current_score)
            sys.stdout.write(f'\r{bar} {format(percents, "2.0f")} %\t {score_string}')
            sys.stdout.flush()
            self.last_score = current_score

    def get_score_string(self, current_score):
        improved = self.last_score and self.last_score < current_score
        score_string = f'[current score {self.OKGREEN if improved else self.ENDC}{current_score}{self.ENDC}]'
        return score_string

    def get_bar(self, filled_len):
        filled_part = (self.OKGREEN + '=' * filled_len + self.ENDC if filled_len > 0 else '')
        return '[' + filled_part + '-' * (self.bar_length - filled_len) + ']'

    def get_percents(self, count):
        return round(float(count) / self.total * 100, 1)

    def get_filled_length(self, count):
        return int(round(self.bar_length * count / float(self.total)))
