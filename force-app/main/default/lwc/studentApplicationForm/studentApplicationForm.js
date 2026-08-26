import { LightningElement, api, track } from 'lwc';
import { ShowToastEvent } from 'lightning/platformShowToastEvent';

export default class StudentApplicationForm extends LightningElement {
    @api recordId;
    @api objectApiName;

    @track firstName = '';
    @track lastName = '';
    @track email = '';
    @track phone = '';
    @track course = '';

    handleInputChange(event) {
        const field = event.target.dataset.id || event.target.name;
        if (field === 'firstName') {
            this.firstName = event.target.value;
        } else if (field === 'lastName') {
            this.lastName = event.target.value;
        } else if (field === 'email') {
            this.email = event.target.value;
        } else if (field === 'phone') {
            this.phone = event.target.value;
        } else if (field === 'course') {
            this.course = event.target.value;
        }
    }

    handleSuccess(event) {
        const evt = new ShowToastEvent({
            title: 'Application Submitted',
            message: 'Student record created successfully. ID: ' + (event.detail ? event.detail.id : ''),
            variant: 'success'
        });
        this.dispatchEvent(evt);
        this.handleReset();
    }

    handleError(event) {
        const evt = new ShowToastEvent({
            title: 'Submission Error',
            message: event.detail && event.detail.detail ? event.detail.detail : 'An unexpected error occurred.',
            variant: 'error'
        });
        this.dispatchEvent(evt);
    }

    handleReset() {
        const inputFields = this.template.querySelectorAll('lightning-input-field');
        if (inputFields) {
            inputFields.forEach((field) => {
                field.reset();
            });
        }
    }
}