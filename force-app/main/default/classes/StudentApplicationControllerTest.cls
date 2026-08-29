@IsTest
private class StudentApplicationControllerTest {

    @IsTest
    static void testSubmitNewApplicationSuccess() {
        StudentApplicationController.ApplicationWrapper wrapper = new StudentApplicationController.ApplicationWrapper();
        wrapper.firstName = 'Jane';
        wrapper.lastName = 'Doe';
        wrapper.email = 'jane.doe@example.com';
        wrapper.phone = '555-0199';
        wrapper.schoolName = 'Highland High';
        wrapper.scholarshipType = 'STEM Leaders Scholarship';
        wrapper.essay = 'I am passionate about science and technology...';

        Test.startTest();
        Id recordId = StudentApplicationController.submitApplication(wrapper);
        Test.stopTest();

        System.assertNotEquals(null, recordId, 'Lead record ID should not be null after submission.');
        Lead createdLead = [SELECT Id, FirstName, LastName, Email, Company, LeadSource FROM Lead WHERE Id = :recordId];
        System.assertEquals('Jane', createdLead.FirstName, 'First Name should match.');
        System.assertEquals('Doe', createdLead.LastName, 'Last Name should match.');
        System.assertEquals('jane.doe@example.com', createdLead.Email, 'Email should match.');
        System.assertEquals('Highland High', createdLead.Company, 'Company/School should match.');
    }

    @IsTest
    static void testSubmitExistingApplicationUpdate() {
        Lead existingLead = new Lead(
            FirstName = 'Jane',
            LastName = 'Doe',
            Email = 'jane.doe@example.com',
            Company = 'Old High School',
            Status = 'Open - Not Contacted'
        );
        insert existingLead;

        StudentApplicationController.ApplicationWrapper wrapper = new StudentApplicationController.ApplicationWrapper();
        wrapper.firstName = 'Jane';
        wrapper.lastName = 'Doe';
        wrapper.email = 'jane.doe@example.com';
        wrapper.phone = '555-0199';
        wrapper.schoolName = 'Updated Academy';
        wrapper.scholarshipType = 'Academic Excellence Scholarship';
        wrapper.essay = 'Updated essay details...';

        Test.startTest();
        Id recordId = StudentApplicationController.submitApplication(wrapper);
        Test.stopTest();

        System.assertEquals(existingLead.Id, recordId, 'Record ID should match existing lead.');
        Lead updatedLead = [SELECT Id, Company FROM Lead WHERE Id = :recordId];
        System.assertEquals('Updated Academy', updatedLead.Company, 'Company should be updated.');
    }

    @IsTest
    static void testSubmitApplicationNullDataValidation() {
        Test.startTest();
        try {
            StudentApplicationController.submitApplication(null);
            System.assert(false, 'Expected AuraHandledException was not thrown.');
        } catch (AuraHandledException e) {
            System.assert(true, 'Exception properly thrown for null application data.');
        }
        Test.stopTest();
    }

    @IsTest
    static void testSubmitApplicationMissingRequiredFields() {
        StudentApplicationController.ApplicationWrapper wrapper = new StudentApplicationController.ApplicationWrapper();
        wrapper.firstName = 'Jane';

        Test.startTest();
        try {
            StudentApplicationController.submitApplication(wrapper);
            System.assert(false, 'Expected AuraHandledException was not thrown.');
        } catch (AuraHandledException e) {
            System.assert(true, 'Exception properly thrown for missing required fields.');
        }
        Test.stopTest();
    }

    @IsTest
    static void testGetScholarshipTypes() {
        Test.startTest();
        List<String> types = StudentApplicationController.getScholarshipTypes();
        Test.stopTest();

        System.assertNotEquals(null, types, 'Scholarship types list should not be null.');
        System.assert(types.size() > 0, 'Scholarship types list should contain items.');
    }
}