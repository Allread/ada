import pulp
import json
import optimizer


def print_help():
    print("Please enter a supported command ('!min', '!max', !items, 'exit', '!exit').")


def main():
    opt = optimizer.Optimizer()

    print_help()
    while True:
        inputs = str.split(input(), ' ')
        if len(inputs) == 0:
            continue
        command = inputs[0]
        args = inputs[1:]

        if command == "exit" or command == '!exit':
            return
        elif command == "!min":
            print(opt.cmd_min(*args))
        elif command == "!max":
            print(opt.cmd_max(*args))
        elif command == "!items":
            print(opt.cmd_items(*args))
        else:
            print_help()


if __name__ == "__main__":
    print("Welcome to the Satisfoptimizer!")
    main()
    print("Goodbye")
