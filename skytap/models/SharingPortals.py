"""Support for sharing portals (were called published sets) that are attached to VMs and environments."""
from skytap.framework.ApiClient import ApiClient
import skytap.framework.Utils as Utils
from skytap.models.SharingPortal import SharingPortal
from skytap.models.SkytapGroup import SkytapGroup


class SharingPortals(SkytapGroup):

    """A collection of notes."""

    def __init__(self, portal_json, env_url):
        """Build Portal list."""
        super(SharingPortals, self).__init__()
        self.load_list_from_json(portal_json, SharingPortal)
        self.url = env_url + '/published_sets.json'

    def add(self, portal):
        """Add one sharing portal.

        Args:
            note (str): The note text to add.

        Returns:
            str: The response from Skytap, typically the new note.
        """
        Utils.info('Adding note: ' + note)
        api = ApiClient()
        data = {"text": note}
        response = api.rest(self.url, data, 'POST')
        self.refresh()
        return response

    def delete(self, portal):
        """Delete one portal.

        Args:
            portal: The :class:`~skytap.models.SharingPortal` to delete.
            - or -
            portal: a string or integer indicating the ID of the class to delete.

        Returns:
            str: The response from Skytap.

        Raises:
            TypeError: If portal is not a SharingPortal, string, or Int object.
        """
        if portal is None:
            return False
        if isinstance(portal, SharingPortal):
            del_id = portal.id
        elif isinstance(portal, str):
            del_id = portal
        elif isinstance(portal, int):
            del_id = str(portal)
        else:
            raise TypeError

        Utils.info('Deleting portal ID: ' + del_id)
        api = ApiClient()
        url = self.url.replace('.json', '/' + del_id)
        response = api.rest(url,
                            {},
                            'DELETE')
        self.refresh()
        return response

    def delete_all(self):
        """Delete all portals.

        Returns:
            int: count of deleted portals.

        Use with care!
        """
        Utils.debug('Deleting all portals.')
        keys = self.data.keys()
        count = len(keys)
        for key in keys:
            self.delete(self.data[key])
        self.refresh()
        return count

    def refresh(self):
        """Refresh the portals.

        Raises:
            KeyError: if the SharingPortal object doesn't
                have a url attribute for some reason.

        Go back to Skytap and get the portals again. Useful when you've changed
        the portals and to make sure you're current.
        """
        if len(self.url) == 0:
            return KeyError
        api = ApiClient()
        portal_json = api.rest(self.url)
        self.load_list_from_json(portal_json, SharingPortal)
