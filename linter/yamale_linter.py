from strictyaml import load, Map, Str, Int, Seq, YAMLError, MapPattern
import argparse

def main():
    parser = argparse.ArgumentParser(description='Validate yaml files.')
    parser.add_argument('path', metavar='PATH', default='./', nargs='?',
                        help='folder to validate. Default is current directory.')
    parser.add_argument('-s', '--schema', default='schema.yaml',
                        help='filename of schema. Default is schema.yaml.')
    args = parser.parse_args()



    schema = Map({"versions": MapPattern(Str(), Map({"folder": Str()}), minimum_keys=1)})

    try:
        with open(args.path) as f:
            person = load(f.read(), schema)
    except YAMLError as error:
        print(error)

    # try:
    #     schema = yamale.make_schema(args.schema)
    #     data = yamale.make_data(args.path)
    #     yamale.validate(schema, data)
    # except YamaleError as e:
    #     for r in e.results:
    #         file_path = r.data
    #         for e in r.errors:
    #             print(f"::warning file={file_path},line=1::{e}")
    #     exit(2)
    # except (SyntaxError, NameError, TypeError, ValueError) as e:
    #     print('Validation failed!\n%s' % str(e))
    #     exit(1)
    # print('Validation success!')



if __name__ == '__main__':
    main()
