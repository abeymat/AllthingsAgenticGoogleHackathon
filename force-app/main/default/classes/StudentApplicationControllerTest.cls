@IsTest
private class StudentApplicationControllerTest {

    @IsTest
    static void testSubmitApplicationSuccess() {
        Map<String, Object> formData = new Map<String, Object>{
            'firstName' => 'Jane',
            'lastName' => 'Doe',
            'email' => 'jane.doe@example.com',
            'phone' => '555-0199',
            'major' => 'Computer Science',
            'gpa' => 3.85,
            'scholarshipType' => 'Academic Excellence',
            'statementOfPurpose' => 'I am passionate about technology and software engineering.'
        };

        Test.startTest();
        String contactId = StudentApplicationController.submitApplication(formData);
        Test.stopTest();

        System.assertNotEquals(null, contactId, 'Returned contact ID should not be null.');

        Contact createdContact = [SELECT Id, FirstName, LastName, Email, Phone, Description FROM Contact WHERE Id = :contactId];
        System.assertEquals('Jane', createdContact.FirstName, 'First name should match input.');
        System.assertEquals('Doe', createdContact.LastName, 'Last name should match input.');
        System.assertEquals('jane.doe@example.com', createdContact.Email, 'Email should match input.');
        System.assert(createdContact.Description.contains('Computer Science'), 'Description should contain major.');
        System.assert(createdContact.Description.contains('3.85'), 'Description should contain GPA.');
    }

    @IsTest
    static void testSubmitApplicationMissingRequiredFields() {
        Map<String, Object> formData = new Map<String, Object>{
            'firstName' => 'John',
            'lastName' => '',
            'email' => ''
        };

        Boolean exceptionThrown = false;
        Test.startTest();
        try {
            StudentApplicationController.submitApplication(formData);
        } catch (AuraHandledException e) {
            exceptionThrown = true;
        }
        Test.stopTest();

        System.assertEquals(true, exceptionThrown, 'An AuraHandledException should be thrown when required fields are missing.');
    }

    @IsTest
    static void testSubmitApplicationEmptyForm() {
        Boolean exceptionThrown = false;
        Test.startTest();
        try {
            StudentApplicationController.submitApplication(null);
        } catch (AuraHandledException e) {
            exceptionThrown = true;
        }
        Test.stopTest();

        System.assertEquals(true, exceptionThrown, 'An AuraHandledException should be thrown for null input.');
    }
}