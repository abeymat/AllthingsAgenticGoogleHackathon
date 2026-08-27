@IsTest
private class StudentApplicationControllerTest {
    @IsTest
    static void testSubmitApplication() {
        Test.startTest();
        String contactId = StudentApplicationController.submitApplication('Jane', 'Doe', 'jane@university.edu');
        Test.stopTest();
        System.assertNotEquals(null, contactId, 'Contact ID should be generated');
    }
}