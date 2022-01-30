import sys
import re


#253976
class Converter:

    @staticmethod
    def convert_binary_to_string1(bin):#every 8bit is separated with zero
        msg = ''
        while len(bin) > 7:
            if(int(bin[:8],2) != 0):
                letter = (chr(int(bin[:8],2)))
                msg += letter
                bin = bin[9:]
            else:
                break
        print(msg)
        return msg

    @staticmethod
    def convert_binary_to_string2(bin):#continuous binary file
        msg = ''
        while len(bin) > 7:
            if(int(bin[:8],2) != 0):
                letter = (chr(int(bin[:8],2)))
                msg += letter
                bin = bin[8:]
            else:
                break
        print(msg)
        return msg

class Message:

    @staticmethod
    def read_in_bytes_message_content(file):
        with open(file, "r") as f:
            msg = f.readline()
            new_msg = " ".join(format(i, '08b') for i in bytearray(msg, encoding='utf-8'))
        return new_msg

    @staticmethod
    def write_detect_message(msg, file):
        with open(file, "w") as f:
            f.write(msg)


class HtmlFile:
    @staticmethod
    def read_line_to_dict(file):
        lines = {}
        i = 0
        with open(file, "r", encoding="utf-8") as f:
            for line in f:
                lines[i] = line.replace('\n', '')
                i += 1
        return lines

    @staticmethod
    def calculate_lines(lines):
        return len(lines)

    @staticmethod
    def calculate_attributes(lines, attr):
        attributes_count = 0
        for key in lines.keys():
            attributes = re.findall(attr, lines[key])
            if attributes:
                attributes_count += len(attributes)
        return attributes_count

    @staticmethod
    def write_lines_from_dict_to_html(text_dict, output_file):
        with open(output_file, "w") as f:
            for key in text_dict.keys():
                f.write(text_dict[key] + "\n")


class NotEnoughLines(Exception):
    def __init__(self, msg_len, l_num):
        super().__init__(
            "Not enough lines in html file to encode message msg len: {}, html lines: {}"
            .format(msg_len, l_num)
        )
        self.msg_len = msg_len
        self.lines_num = l_num


class NotEnoughAttributes(Exception):
    def __init__(self, msg_len, attributes_num):
        super().__init__(
            "Not enough specified attributes in html file to encode message msg len: {}, html attributes: {}"
            .format(msg_len, attributes_num)
        )
        self.msg_len = msg_len
        self.attributes_num = attributes_num


class NotEnoughSpaces(Exception):
    def __init__(self, msg_len, spaces_num):
        super().__init__(
            "Not enough specified single spaces in html file to encode message msg len: {}, number of spaces: {}"
            .format(msg_len, spaces_num)
        )
        self.msg_len = msg_len
        self.spaces_num = spaces_num


class SingleEndingSpace:
    @staticmethod
    def add_ending_lines_spaces(msg, dict_text):
        dict_with_encoded_spaces = dict_text.copy()
        for bit in range(len(msg)):
            if msg[bit] == '1':
                dict_with_encoded_spaces[bit] = dict_text[bit] + ' '
        return dict_with_encoded_spaces

    @staticmethod
    def decode_ending_lines_spaces(watermark_dict):
        decoded_msg = ''
        for key in watermark_dict.keys():
            if watermark_dict[key][len(watermark_dict[key]) - 1] == " ":
                decoded_msg += '1'
            else:
                decoded_msg += '0'
        return decoded_msg


class AttributesTypos:
    @staticmethod
    def find_all_attributes_spans(dict_text, attr):
        dict_with_attr = {}
        for key in dict_text.keys():
            attributes = re.findall(attr, dict_text[key])
            if attributes:
                iterator = re.finditer(attr, dict_text[key])
                matches = []
                for match in iterator:
                    matches.append(match.span())
                dict_with_attr[key] = matches
        return dict_with_attr

    @staticmethod
    def add_attributes_typos(msg, dict_text, attr, attr_one, attr_zero):
        dict_with_attr_positions = AttributesTypos.find_all_attributes_spans(dict_text, attr)
        attr_keys = [key for key in dict_with_attr_positions.keys()]
        result_dict = dict_text.copy()
        k = 0
        i = 0
        for bit in msg:
            next_key = attr_keys[k]
            if bit == '1':
                result_dict[next_key] = dict_text[next_key].replace(
                    attr,
                    attr_one,
                    1
                )
            elif bit == '0':
                result_dict[next_key] = dict_text[next_key].replace(
                    attr,
                    attr_zero,
                    1
                )
            if i == len(dict_with_attr_positions[next_key]) - 1:
                i = 0
                k += 1
            else:
                i += 1
        return result_dict

    @staticmethod
    def sort_attr_list(list_of_lists):
        for i in range(len(list_of_lists)-1,0,-1):
            for j in range(i):
                if list_of_lists[j][0] > list_of_lists[j+1][0]:
                    temp = list_of_lists[j]
                    list_of_lists[j] = list_of_lists[j+1]
                    list_of_lists[j+1] = temp
        return list_of_lists

    @staticmethod
    def decode_attributes_typos(watermark_dict, attr_one, attr_zero):
        decoded_msg = ''
        for key in watermark_dict.keys():
            bits = []
            spans = []
            one = re.findall(attr_one, watermark_dict[key])
            zero = re.findall(attr_zero, watermark_dict[key])
            if zero:
                iterator = re.finditer(attr_zero, watermark_dict[key])
                for match in iterator:
                    bits.append([match.span()[0], '0'])
                    spans.append(match.span()[0])
            if one:
                iterator = re.finditer(attr_one, watermark_dict[key])
                for match in iterator:
                    if match.span()[0] not in spans:
                        bits.append([match.span()[0], '1'])
            bits = AttributesTypos.sort_attr_list(bits)
            for match in bits:
                decoded_msg += match[1]
        return decoded_msg


class DoubleSpace:
    @staticmethod
    def add_double_spaces(msg, dict_text):
        dict_with_spaces_positions = AttributesTypos.find_all_attributes_spans(dict_text, ' ')
        spaces_keys = [key for key in dict_with_spaces_positions.keys()]
        result_dict = dict_text.copy()
        k = 0
        i = 0
        span_shift = 0
        for bit in msg:
            next_key = spaces_keys[k]
            if bit == '1':
                matching_span = dict_with_spaces_positions[next_key][i][0]
                result_dict[next_key] = result_dict[next_key][:matching_span + span_shift] + ' ' + result_dict[next_key][matching_span + span_shift:]
                span_shift += 1
            if i == len(dict_with_spaces_positions[next_key]) - 1:
                i = 0
                k += 1
                span_shift = 0
            else:
                i += 1
        return result_dict

    @staticmethod
    def decode_double_spaces(watermark_dict):
        decoded_msg = ''
        for key in watermark_dict.keys():
            bits = []
            spans = []
            one = re.findall('  ', watermark_dict[key])
            zero = re.findall(' ', watermark_dict[key])
            if one:
                iterator = re.finditer('  ', watermark_dict[key])
                for match in iterator:
                    bits.append([match.span()[0], '1'])
                    spans.append(match.span()[0])
            if zero:
                iterator = re.finditer(' ', watermark_dict[key])
                for match in iterator:
                    m = match.span()[0]
                    if m not in spans and m - 1 not in spans and m + 1 not in spans:
                        bits.append([match.span()[0], '0'])
            bits = AttributesTypos.sort_attr_list(bits)
            for match in bits:
                decoded_msg += match[1]
        return decoded_msg


if __name__ == "__main__":
    if sys.argv[1] == '-e':
        message = Message.read_in_bytes_message_content("mess.txt")
        print(message)
        d = HtmlFile.read_line_to_dict("cover.html")
        if sys.argv[2] == '-1':
            lines_num = HtmlFile.calculate_lines(d)
            if len(message) > lines_num:
                raise NotEnoughLines(len(message), lines_num)
            encoded = SingleEndingSpace.add_ending_lines_spaces(message, d)
            HtmlFile.write_lines_from_dict_to_html(encoded, "watermark.html")
        elif sys.argv[2] == '-2':
            spaces_number = HtmlFile.calculate_attributes(d, ' ')
            if len(message) > spaces_number:
                raise NotEnoughSpaces(len(message), spaces_number)
            encoded = DoubleSpace.add_double_spaces(message, d)
            HtmlFile.write_lines_from_dict_to_html(encoded, "watermark.html")
        elif sys.argv[2] == '-3':
            attribute = 'style="margin-bottom: 0cm; line-height: 100%"'
            attribute_one = 'style="margin-bottom: 0cm; lineheight: 100%"'
            attribute_zero = 'style="margin-botom: 0cm; line-height: 100%"'
            attr_num = HtmlFile.calculate_attributes(d, attribute)
            if len(message) > attr_num:
                raise NotEnoughAttributes(len(message), attr_num)
            encoded = AttributesTypos.add_attributes_typos(message, d, attribute, attribute_one, attribute_zero)
            HtmlFile.write_lines_from_dict_to_html(encoded, "watermark.html")
        elif sys.argv[2] == '-4':
            attribute = '</font>'
            attribute_zero = '</font><font></font>'
            attribute_one = '</font><font>'
            attr_num = HtmlFile.calculate_attributes(d, attribute)
            if len(message) > attr_num:
                raise NotEnoughAttributes(len(message), attr_num)
            encoded = AttributesTypos.add_attributes_typos(message, d, attribute, attribute_one, attribute_zero)
            HtmlFile.write_lines_from_dict_to_html(encoded, "watermark.html")

    if sys.argv[1] == '-d':
        d = HtmlFile.read_line_to_dict("watermark.html")
        if sys.argv[2] == '-1':
            decoded = SingleEndingSpace.decode_ending_lines_spaces(d)
            print(decoded)
            decoded = Converter.convert_binary_to_string1(decoded)
            Message.write_detect_message(decoded, "detected.txt")
        elif sys.argv[2] == '-2':
            decoded = DoubleSpace.decode_double_spaces(d)
            print(decoded)
            decoded = Converter.convert_binary_to_string1(decoded)
            Message.write_detect_message(decoded, "detected.txt")
        elif sys.argv[2] == '-3':
            attribute_one = 'style="margin-bottom: 0cm; lineheight: 100%"'
            attribute_zero = 'style="margin-botom: 0cm; line-height: 100%"'
            decoded = AttributesTypos.decode_attributes_typos(d, attribute_one, attribute_zero)
            print(decoded)
            decoded = Converter.convert_binary_to_string2(decoded)
            Message.write_detect_message(decoded, "detected.txt")
        elif sys.argv[2] == '-4':
            attribute_zero = '</font><font></font>'
            attribute_one = '</font><font>'
            decoded = AttributesTypos.decode_attributes_typos(d, attribute_one, attribute_zero)
            print(decoded)
            decoded = Converter.convert_binary_to_string2(decoded)
            Message.write_detect_message(decoded, "detected.txt")
