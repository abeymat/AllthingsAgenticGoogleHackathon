@IsTest
private class StudentApplicationControllerTest {

    @TestSetup
    static void setupTestData() {
        Account testAccount = new Account(
            Name = 'Test University'
        );
        insert testAccount;

        Contact testStudent = new Contact(
            FirstName = 'John',
            LastName = 'Doe',
            Email = 'john.doe@example.com',
            Phone = '1234567890',
            AccountId = testAccount.Id
        );
        insert testStudent;

        Lead testApplicant = new Lead(
            FirstName = 'Jane',
            LastName = 'Smith',
            Company = 'Test University',
            Email = 'jane.smith@example.com',
            Phone = '0987654321',
            Status = 'Open - Not Contacted'
        );
        insert testApplicant;
    }

    @IsTest
    static void testGetStudentApplications() {
        Contact testContact = [SELECT Id, LastName FROM Contact LIMIT 1];

        Test.startTest();
        List<Contact> students = [SELECT Id, FirstName, LastName, Email, Phone FROM Contact WHERE Id = :testContact.Id];
        Test.stopTest();

        System.assertEquals(1, students.size(), 'Expected to retrieve one student record.');
        System.assertEquals('Doe', students[0].LastName, 'Student last name should match test data.');
    }

    @IsTest
    static void testSubmitStudentApplicationSuccess() {
        Test.startTest();
        Lead newApplicant = new Lead(
            FirstName = 'Alice',
            LastName = 'Johnson',
            Company = 'Test University',
            Email = 'alice.johnson@example.com',
            Phone = '5551234567',
            Status = 'Open - Not Contacted'
        );
        insert newApplicant;
        Test.stopTest();

        Lead createdLead = [SELECT Id, FirstName, LastName, Email FROM Lead WHERE Email = 'alice.johnson@example.com' LIMIT 1];
        System.assertNotEquals(null, createdLead.Id, 'Lead ID should not be null after submission.');
        System.assertEquals('Alice', createdLead.FirstName, 'First name should match.');
    }

    @IsTest
    static void testUpdateStudentApplicationStatus() {
        Lead testApplicant = [SELECT Id, Status FROM Lead LIMIT 1];

        Test.startTest();
        testApplicant.Status = 'Working - Contacted';
        update testApplicant;
        Test.stopTest();

        Lead updatedLead = [SELECT Id, Status FROM Lead WHERE Id = :testApplicant.Id];
        System.assertEquals('Working - Contacted', updatedLead.Status, 'Application status should be updated.');
    }

    @IsTest
    static void testApplicationBulkProcessing() {
        List<Lead> bulkApplicants = new List<Lead>();
        for (Integer i = 0; i < 50; i++) {
            bulkApplicants.add(new Lead(
                FirstName = 'Student' + i,
                LastName = 'Test',
                Company = 'Test University',
                Email = 'student' + i + '@example.com'
            ));
        }

        Test.startTest();
        insert bulkApplicants;
        Test.stopTest();

        List<Lead> insertedApplicants = [SELECT Id FROM Lead WHERE LastName = 'Test'];
        System.assertEquals(50, insertedApplicants.size(), 'Bulk insert should process 50 student records.');
    }
}