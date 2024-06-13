import unittest
from unittest.mock import patch, MagicMock
import boxapicall

class TestBoxApiCall(unittest.TestCase):

    @patch('boxapicall.Client')
    def test_upload_file(self, MockClient):
        mock_client = MockClient.return_value
        mock_folder = MagicMock()
        mock_client.folder.return_value.get.return_value = mock_folder
        mock_file = MagicMock()
        mock_folder.upload.return_value = mock_file

        result = boxapicall.upload_file(mock_client, '0', 'test_file.txt')
        self.assertEqual(result, "SUCCESS")
        mock_folder.upload.assert_called_with('test_file.txt')

    @patch('boxapicall.Client')
    def test_list_files(self, MockClient):
        mock_client = MockClient.return_value
        mock_folder = MagicMock()
        mock_client.folder.return_value.get.return_value = mock_folder
        mock_file = MagicMock()
        mock_file.type = 'file'
        mock_file.name = 'test_file.txt'
        mock_file.id = '12345'
        mock_folder.get_items.return_value = [mock_file]

        with patch('builtins.print') as mocked_print:
            result = boxapicall.list_files(mock_client, '0')
            self.assertEqual(result, "SUCCESS")
            mocked_print.assert_called_with('File: test_file.txt, ID: 12345')

    @patch('boxapicall.Client')
    def test_list_directories(self, MockClient):
        mock_client = MockClient.return_value
        mock_folder = MagicMock()
        mock_client.folder.return_value.get.return_value = mock_folder
        mock_directory = MagicMock()
        mock_directory.type = 'folder'
        mock_directory.name = 'test_folder'
        mock_directory.id = '12345'
        mock_folder.get_items.return_value = [mock_directory]

        with patch('builtins.print') as mocked_print:
            result = boxapicall.list_directories(mock_client, '0')
            self.assertEqual(result, "SUCCESS")
            mocked_print.assert_called_with('Directory: test_folder, ID: 12345')

    @patch('boxapicall.Client')
    def test_list_all_directories(self, MockClient):
        mock_client = MockClient.return_value
        mock_folder = MagicMock()
        mock_client.folder.return_value.get.return_value = mock_folder
        mock_directory = MagicMock()
        mock_directory.type = 'folder'
        mock_directory.name = 'test_folder'
        mock_directory.id = '12345'
        mock_folder.get_items.return_value = [mock_directory]

        with patch('builtins.print') as mocked_print:
            result = boxapicall.list_all_directories(mock_client, '0')
            self.assertEqual(result, "SUCCESS")
            mocked_print.assert_any_call('Directory: test_folder, ID: 12345')

    @patch('boxapicall.Client')
    @patch('builtins.open', new_callable=unittest.mock.mock_open)
    def test_download_file(self, mock_open, MockClient):
        mock_client = MockClient.return_value
        mock_file = MagicMock()
        mock_client.file.return_value.get.return_value = mock_file

        result = boxapicall.download_file(mock_client, '12345', 'test_file.txt')
        self.assertEqual(result, "SUCCESS")
        mock_file.download_to.assert_called()
        mock_open.assert_called_with('test_file.txt', 'wb')

if __name__ == '__main__':
    unittest.main()