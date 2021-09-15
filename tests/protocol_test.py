import struct
import pytest
from src.pydevlpr_protocol import DataTopic, wrap_packet, unwrap_packet, unpack_serial, DataFormatException, PacketType

class TestWrap:
    def test_unsupported_msg(self):
        msg_type = "error"
        pin = 0
        msg = 100
        with pytest.raises(DataFormatException):
            wrap_packet(msg_type, pin, msg)

    def test_nominal_data_topics(self):
        topics = DataTopic.topics()
        pin = 0
        msg = 100
        for msg_type in topics:
            assert len(msg_type) == 2
            packet = wrap_packet(msg_type, pin, msg)
            assert "{}|0|100".format(msg_type) == packet

    def test_nominal_packet_types(self):
        packet_types = PacketType.topics()
        topic = DataTopic.RAW_DATA_TOPIC
        for msg_type in packet_types:
            assert len(msg_type) == 1  # Message types should be 1 char
            packet = wrap_packet(msg_type, topic)
            assert "{}|ra".format(msg_type) == packet

class TestUnwrap:
    def test_fail_invalid_topic(self):
        msg = "zz|3|10"
        (msg_type, pin, data) = unwrap_packet(msg)
        assert msg_type not in DataTopic.topics()

    def test_nominal_data(self):
        msg = "ra|3|100"
        try:
            (msg_type, pin, data) = unwrap_packet(msg)
        except DataFormatException:
            pytest.fail("Unwrap failed") 
        assert msg_type == "ra"
        assert pin == 3
        assert data == "100"

    def test_nominal_command(self):
        msg = "s|ra"
        try:
            (msg_type, content) = unwrap_packet(msg)
        except DataFormatException:
            pytest.fail("Unwrap failed")
        assert msg_type == "s"
        assert content == "ra"

class TestUnpack:
    def test_nominal(self):
        byte_array = [0xDE, 0xFE, 0xCC]
        try:
            (pin, data) = unpack_serial(byte_array)
        except DataFormatException:
            pytest.fail("Unpack failed")
        assert pin == 3
        assert data == struct.unpack(">h", bytes([0xDF,0xFF]))[0]

if __name__ == "__main__":
    pytest.main()