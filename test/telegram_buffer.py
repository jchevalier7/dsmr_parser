from unittest import mock, TestCase
from unittest.mock import call

from dsmr_parser.serial import TelegramBuffer
from test.example_telegrams import TELEGRAM_V2_2, TELEGRAM_V4_2


class TelegramBufferTest(TestCase):

    def setUp(self):
        self.callback = mock.MagicMock()
        self.telegram_buffer = TelegramBuffer(self.callback)

    def test_v22_telegram(self):
        self.telegram_buffer.append(TELEGRAM_V2_2)

        self.callback.assert_called_once_with(TELEGRAM_V2_2)
        self.assertEqual(self.telegram_buffer._buffer, '')

    def test_v42_telegram(self):
        self.telegram_buffer.append(TELEGRAM_V4_2)

        self.callback.assert_called_once_with(TELEGRAM_V4_2)
        self.assertEqual(self.telegram_buffer._buffer, '')

    def test_multiple_mixed_telegrams(self):
        self.telegram_buffer.append(
            ''.join((TELEGRAM_V2_2, TELEGRAM_V4_2, TELEGRAM_V2_2))
        )

        self.callback.assert_has_calls([
            call(TELEGRAM_V2_2),
            call(TELEGRAM_V4_2),
            call(TELEGRAM_V2_2),
        ])
        self.assertEqual(self.telegram_buffer._buffer, '')

    def test_v42_telegram_preceded_with_unclosed_telegram(self):
        # There are unclosed telegrams at the start of the buffer.
        incomplete_telegram = TELEGRAM_V4_2[:-1]

        self.telegram_buffer.append(incomplete_telegram + TELEGRAM_V4_2)

        self.callback.assert_called_once_with(TELEGRAM_V4_2)
        self.assertEqual(self.telegram_buffer._buffer, '')

    def test_v42_telegram_preceded_with_unopened_telegram(self):
        # There is unopened telegrams at the start of the buffer indicating that
        # the buffer was being filled while the telegram was outputted halfway.
        incomplete_telegram = TELEGRAM_V4_2[1:]

        self.telegram_buffer.append(incomplete_telegram + TELEGRAM_V4_2)

        self.callback.assert_called_once_with(TELEGRAM_V4_2)
        self.assertEqual(self.telegram_buffer._buffer, '')

    def test_v42_telegram_trailed_by_unclosed_telegram(self):
        incomplete_telegram = TELEGRAM_V4_2[:-1]

        self.telegram_buffer.append(TELEGRAM_V4_2 + incomplete_telegram)

        self.callback.assert_called_once_with(TELEGRAM_V4_2)
        self.assertEqual(self.telegram_buffer._buffer, incomplete_telegram)

    def test_v42_telegram_trailed_by_unopened_telegram(self):
        incomplete_telegram = TELEGRAM_V4_2[1:]

        self.telegram_buffer.append(TELEGRAM_V4_2 + incomplete_telegram)

        self.callback.assert_called_once_with(TELEGRAM_V4_2)
        self.assertEqual(self.telegram_buffer._buffer, incomplete_telegram)

    def test_v42_telegram_adding_line_by_line(self):
        for line in TELEGRAM_V4_2.splitlines(keepends=True):
            self.telegram_buffer.append(line)

        self.callback.assert_called_once_with(TELEGRAM_V4_2)
        self.assertEqual(self.telegram_buffer._buffer, '')

    def test_v42_telegram_adding_char_by_char(self):
        for char in TELEGRAM_V4_2:
            self.telegram_buffer.append(char)

        self.callback.assert_called_once_with(TELEGRAM_V4_2)
        self.assertEqual(self.telegram_buffer._buffer, '')